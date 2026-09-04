from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[3]
VOLUME = ROOT / "production" / "reimaginings" / "ember-lattice" / "volume"
THRESHOLDS = {3: 100, 4: 140, 5: 190, 6: 250, 7: 320, 8: 400}
LEVEL_GROWTH = {4: (4, 0), 5: (6, 0), 6: (6, 2), 7: (7, 4), 8: (8, 4)}  # HP max, Qi max
TIMES = {
    1:"00:00–00:18",2:"00:18–00:52",3:"00:52–02:05",4:"02:05–02:31",5:"02:31–05:10",
    6:"05:10–06:42",7:"06:42–07:11",8:"07:11–08:26",9:"08:26–11:30",10:"11:30–14:00",
}


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def item(name: str, qty: int, rarity: str, weight: int, condition: str, provenance: str) -> dict[str, Any]:
    return {"name":name,"quantity":qty,"rarity":rarity,"weight":weight,"condition":condition,"provenance":provenance}


def initial_state() -> dict[str, Any]:
    return {
        "entity_id":"char-elian", "level":3, "xp":60, "next_threshold":100, "unspent_points":0,
        "stats":{"force":6,"step":8,"sense":9,"guard":5},
        "hp":{"current":44,"max":52}, "qi":{"current":31,"max":40},
        "class":"Salvager", "class_history":["Salvager"],
        "cultivation":"Breath Seed I", "cultivation_history":["Breath Seed I"],
        "skills":{
            "fault-sight":{"name":"Fault Sight","rank":1,"cost":12,"resource":"Qi","cooldown_seconds":20,"condition":"one verified stress line","source":"damaged survey lens training"}
        },
        "statuses":[], "injuries":[],
        "equipment":{"main_hand":"Hooked Shortblade","body":"Frayed Salvager Coat","utility":None},
        "inventory":{
            "spark-talisman":item("Spark Talisman",1,"Tempered",1,"intact","starting salvage"),
            "iron-seal":item("Iron Seal",2,"Common",1,"intact","starting salvage"),
        },
        "currency":{"brass_marks":12},
        "quests":{"bridge-that-bites":"ACTIVE"},
        "dungeon":{"zone":"Ember Vault","cleared":[]},
        "boss_credit":[],
        "factions":{"Free Delvers":0,"Ash Crown":0}, "party_trust":3,
        "party":{
            "char-mira":{"level":5,"class":"Bastion Lancer","skills":{"rampart-thrust":2},"equipment":{"shield":"Ivory Split Shield","main_hand":"Dark-Teal Spear"},"injuries":[]},
            "char-orin":None,
            "char-sable":None,
        },
        "irreversible":[],
    }


class Ledger:
    def __init__(self, state: dict[str, Any], chapter: int):
        self.state = state
        self.chapter = chapter
        self.transactions: list[dict[str, Any]] = []

    def add(self, panel: int, kind: str, **data: Any) -> None:
        self.transactions.append({"panel_id":f"el-ch{self.chapter:02d}-s01-p{panel:03d}","type":kind,**data})

    def resource(self, panel: int, resource: str, amount: int, provenance: str) -> None:
        pool = self.state[resource]
        before = pool["current"]
        after = max(0, min(pool["max"], before + amount))
        actual = after - before
        pool["current"] = after
        self.add(panel,"resource",resource=resource,amount=actual,before=before,after=after,provenance=provenance)

    def resource_max(self, panel: int, resource: str, amount: int, restore: int, provenance: str) -> None:
        pool = self.state[resource]
        before_max, before_current = pool["max"], pool["current"]
        pool["max"] += amount
        pool["current"] = min(pool["max"], pool["current"] + restore)
        self.add(panel,"resource_max",resource=resource,max_before=before_max,max_after=pool["max"],current_before=before_current,current_after=pool["current"],restore=restore,provenance=provenance)

    def xp(self, panel: int, amount: int, provenance: str) -> None:
        before_level, before_xp = self.state["level"], self.state["xp"]
        self.state["xp"] += amount
        level_events = []
        while self.state["xp"] >= THRESHOLDS[self.state["level"]]:
            threshold = THRESHOLDS[self.state["level"]]
            self.state["xp"] -= threshold
            self.state["level"] += 1
            new_level = self.state["level"]
            hp_growth, qi_growth = LEVEL_GROWTH[new_level]
            self.state["hp"]["max"] += hp_growth
            self.state["qi"]["max"] += qi_growth
            self.state["unspent_points"] += 1
            level_events.append({"from":new_level-1,"to":new_level,"threshold":threshold,"hp_max_gain":hp_growth,"qi_max_gain":qi_growth,"point_gain":1})
        self.state["next_threshold"] = THRESHOLDS[self.state["level"]]
        self.add(panel,"xp_gain",amount=amount,level_before=before_level,xp_before=before_xp,level_after=self.state["level"],xp_after=self.state["xp"],next_threshold=self.state["next_threshold"],level_events=level_events,provenance=provenance)

    def spend_point(self, panel: int, stat: str, amount: int, provenance: str) -> None:
        if self.state["unspent_points"] < amount:
            raise ValueError("insufficient unspent points")
        before = self.state["stats"][stat]
        self.state["unspent_points"] -= amount
        self.state["stats"][stat] += amount
        self.add(panel,"attribute_spend",stat=stat,amount=amount,before=before,after=self.state["stats"][stat],unspent_after=self.state["unspent_points"],provenance=provenance)

    def gain_item(self, panel: int, item_id: str, name: str, qty: int, rarity: str, weight: int, provenance: str, condition: str="intact") -> None:
        before = self.state["inventory"].get(item_id, {}).get("quantity",0)
        if item_id not in self.state["inventory"]:
            self.state["inventory"][item_id] = item(name,0,rarity,weight,condition,provenance)
        self.state["inventory"][item_id]["quantity"] += qty
        self.state["inventory"][item_id]["condition"] = condition
        self.add(panel,"item_gain",item_id=item_id,name=name,rarity=rarity,amount=qty,before=before,after=before+qty,condition=condition,provenance=provenance)

    def consume_item(self, panel: int, item_id: str, qty: int, provenance: str, action: str="consume") -> None:
        row = self.state["inventory"].get(item_id)
        if not row or row["quantity"] < qty:
            raise ValueError(f"insufficient item {item_id}")
        before = row["quantity"]
        row["quantity"] -= qty
        self.add(panel,f"item_{action}",item_id=item_id,name=row["name"],amount=-qty,before=before,after=row["quantity"],provenance=provenance)

    def item_condition(self, panel: int, item_id: str, condition: str, provenance: str) -> None:
        row = self.state["inventory"][item_id]
        before = row["condition"]
        row["condition"] = condition
        self.add(panel,"item_condition",item_id=item_id,before=before,after=condition,provenance=provenance)

    def equipment(self, panel: int, entity: str, slot: str, value: str | None, provenance: str, condition: str="intact") -> None:
        target = self.state["equipment"] if entity == "char-elian" else self.state["party"][entity]["equipment"]
        before = target.get(slot)
        target[slot] = value
        self.add(panel,"equipment_change",entity_id=entity,slot=slot,before=before,after=value,condition=condition,provenance=provenance)

    def quest(self, panel: int, quest_id: str, new: str, provenance: str) -> None:
        before = self.state["quests"].get(quest_id)
        self.state["quests"][quest_id] = new
        self.add(panel,"quest_state",quest_id=quest_id,before=before,after=new,provenance=provenance)

    def skill(self, panel: int, skill_id: str, name: str, rank: int, cost: int, cooldown: int, condition: str, source: str) -> None:
        before = copy.deepcopy(self.state["skills"].get(skill_id))
        self.state["skills"][skill_id] = {"name":name,"rank":rank,"cost":cost,"resource":"Qi","cooldown_seconds":cooldown,"condition":condition,"source":source}
        self.add(panel,"skill_change",skill_id=skill_id,before=before,after=copy.deepcopy(self.state["skills"][skill_id]),provenance=source)

    def cultivation(self, panel: int, new: str, max_gain: int, restore: int, provenance: str) -> None:
        before = self.state["cultivation"]
        self.state["cultivation"] = new
        self.state["cultivation_history"].append(new)
        self.resource_max(panel,"qi",max_gain,restore,provenance)
        self.add(panel,"cultivation_advance",before=before,after=new,provenance=provenance)

    def class_change(self, panel: int, new: str, provenance: str) -> None:
        before = self.state["class"]
        self.state["class"] = new
        self.state["class_history"].append(new)
        self.add(panel,"class_change",before=before,after=new,provenance=provenance)

    def status_add(self, panel: int, status: str, provenance: str, injury: bool=False) -> None:
        bucket = "injuries" if injury else "statuses"
        if status not in self.state[bucket]:
            self.state[bucket].append(status)
        self.add(panel,"status_add",status=status,bucket=bucket,provenance=provenance)

    def status_remove(self, panel: int, status: str, provenance: str, injury: bool=False) -> None:
        bucket = "injuries" if injury else "statuses"
        if status not in self.state[bucket]:
            raise ValueError(f"missing state {status}")
        self.state[bucket].remove(status)
        self.add(panel,"status_remove",status=status,bucket=bucket,provenance=provenance)

    def faction(self, panel: int, name: str, delta: int, provenance: str) -> None:
        before = self.state["factions"][name]
        self.state["factions"][name] += delta
        self.add(panel,"faction_delta",faction=name,amount=delta,before=before,after=self.state["factions"][name],provenance=provenance)

    def trust(self, panel: int, delta: int, provenance: str) -> None:
        before = self.state["party_trust"]
        self.state["party_trust"] += delta
        self.add(panel,"party_trust",amount=delta,before=before,after=self.state["party_trust"],provenance=provenance)

    def irreversible(self, panel: int, flag: str, provenance: str) -> None:
        self.state["irreversible"].append(flag)
        self.add(panel,"irreversible",flag=flag,provenance=provenance)


def run_chapter(ch: int, state: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    L = Ledger(state, ch)
    if ch == 1:
        L.resource(9,"qi",-12,"Fault Sight I activation")
        L.resource(11,"hp",-22,"Belljaw forelimb impact"); L.status_add(11,"Cracked Rib","Belljaw impact",True)
        L.consume_item(13,"spark-talisman",1,"voluntary catalyst sacrifice")
        L.resource(13,"qi",14,"Spark Talisman")
        L.resource(14,"qi",-30,"Breath Seed II pattern")
        L.cultivation(14,"Breath Seed II",8,8,"danger insight plus Spark Talisman")
        L.skill(14,"fault-step","Fault Step",1,8,8,"one acceleration burst along verified fault","Breath Seed II compatibility")
        L.resource(14,"hp",-1,"Overburn tick 1/2"); L.resource(15,"qi",-8,"Fault Step I")
        L.resource(15,"hp",-1,"Overburn tick 2/2")
        L.xp(16,85,"Belljaw Warden kill share")
        L.gain_item(16,"cinder-key","Cinder-Key",1,"Rare",1,"Belljaw Warden boss drop")
        L.quest(16,"bridge-that-bites","COMPLETED","boss defeated and anchor preserved")
        L.quest(24,"choose-the-crack","OFFERED","Cinder-Key class terminal")
        L.state["dungeon"]["cleared"].append("Ember Vault bridge")
        L.state["boss_credit"].append("Belljaw Warden")
        L.irreversible(16,"Belljaw Warden defeated; one bridge anchor intact","verified clear")
    elif ch == 2:
        L.resource(2,"qi",45,"bell-lift thermal rest")
        L.consume_item(4,"cinder-key",1,"bind Faultline class seal","bind")
        L.class_change(4,"Faultline Adept","owner-approved class path and Cinder-Key")
        L.resource_max(4,"qi",4,0,"Faultline Adept class vessel")
        L.skill(6,"fault-hook","Fault Hook",1,10,12,"self or unsecured object toward verified fault","Faultline Adept selection")
        L.spend_point(6,"sense",1,"class selection allocation")
        L.quest(7,"chainworks-evacuation","ACCEPTED","trapped maintenance delver")
        L.resource(11,"qi",-12,"Fault Sight I"); L.resource(13,"qi",-10,"Fault Hook I"); L.resource(19,"qi",-8,"Fault Step I")
        L.consume_item(16,"iron-seal",1,"stabilize rescue span")
        L.xp(20,55,"Cinder Mite kill share")
        L.gain_item(21,"cinder-carapace","Cinder-Mite Carapace",3,"Common",2,"Cinder Mite drops")
        L.gain_item(21,"chainspool","Chainspool",1,"Tempered",2,"rescued-delver maintenance cache")
        L.xp(24,30,"Chainworks evacuation completion")
        L.quest(24,"chainworks-evacuation","COMPLETED","delver rescued and span stabilized")
        L.faction(24,"Free Delvers",4,"public rescue witness"); L.trust(24,2,"Elian chose person over future seal")
        L.quest(24,"choose-the-crack","COMPLETED","Faultline Adept selected")
        L.irreversible(24,"one Iron Seal spent in Chainworks rescue","stabilized span")
    elif ch == 3:
        L.state["party"]["char-orin"]={"level":6,"class":"Forge-Medic","skills":{"suture-pulse":2,"kiln-quench":1},"equipment":{"utility":"Kiln Satchel"},"injuries":[]}
        L.resource(2,"qi",34,"survey vestibule rest")
        L.consume_item(4,"resin-suture",0,"placeholder") if False else None
        L.gain_item(3,"resin-suture","Resin Suture",1,"Tempered",1,"Orin medical stock")
        L.consume_item(4,"resin-suture",1,"Cracked Rib treatment")
        L.resource(4,"hp",24,"Resin Suture"); L.resource(9,"hp",12,"supervised rest")
        L.status_remove(4,"Cracked Rib","Resin Suture",True)
        L.quest(5,"three-breaths","ACCEPTED","Orin training gate")
        L.xp(10,25,"Three Breaths training completion")
        L.quest(10,"three-breaths","COMPLETED","three-phase form learned")
        L.resource(15,"qi",-12,"Fault Sight I")
        L.resource(17,"hp",-18,"Glassback rail shrapnel"); L.status_add(17,"Right Palm Cut","glass shrapnel",True)
        L.resource(19,"qi",-32,"Breath Seed III gate")
        L.cultivation(19,"Breath Seed III",6,8,"three-note pressure insight with injured hand")
        L.skill(20,"rift-draw","Rift Draw",1,16,30,"one severing arc on verified fault","Breath Seed III")
        L.resource(21,"qi",-16,"Rift Draw I")
        L.xp(22,70,"Glassback Skitter kill share")
        L.gain_item(23,"glass-lens","Glass Lens",1,"Rare",1,"Glassback drop")
        L.gain_item(23,"acid-gland","Verdigris Acid Gland",2,"Tempered",1,"Glassback drop")
        L.faction(24,"Free Delvers",2,"Glass Gallery route cleared")
        L.state["boss_credit"].append("Glassback Skitter"); L.state["dungeon"]["cleared"].append("Glass Gallery")
    elif ch == 4:
        L.state["party"]["char-sable"]={"level":7,"class":"Ash Crown Pathcutter","skills":{"severing-lane":2},"equipment":{"main_hand":"Segmented Saber"},"injuries":[],"ash_debt":4,"party_status":"rival"}
        L.resource(2,"qi",30,"gate approach rest")
        L.quest(4,"claim-verdigris-seal","ACCEPTED","competitive seal contract")
        L.resource(11,"qi",-12,"Fault Sight I"); L.resource(12,"qi",-16,"Rift Draw I")
        L.resource(16,"hp",-26,"Crownspike Bailiff shoulder impact"); L.status_add(16,"Fractured Scapula","Bailiff impact",True)
        L.item_condition(17,"glass-lens","cracked","Bailiff collision")
        L.state["party"]["char-mira"]["equipment"]["main_hand"]="Bent Dark-Teal Spear"
        L.add(15,"equipment_condition",entity_id="char-mira",slot="main_hand",before="intact",after="bent",provenance="Bailiff crown spike")
        L.xp(18,20,"Bailiff migrating-sigil discovery")
        L.quest(19,"claim-verdigris-seal","FAILED","Sable claimed seal first")
        L.faction(19,"Free Delvers",-2,"failed public seal claim"); L.faction(19,"Ash Crown",5,"Sable delivered seal")
        L.trust(23,1,"Mira and Orin extraction under defeat")
        L.irreversible(19,"Sable owns Verdigris Seal; party received no reward","competitive quest result")
    elif ch == 5:
        L.resource(2,"qi",56,"kiln refuge rest")
        L.resource(3,"hp",6,"immobilized rest")
        L.gain_item(3,"stitchfire-ampoule","Stitchfire Ampoule",1,"Rare",1,"Orin reserve stock")
        L.consume_item(6,"stitchfire-ampoule",1,"scapula treatment")
        L.resource(6,"hp",32,"Stitchfire treatment")
        L.status_remove(6,"Fractured Scapula","Stitchfire treatment",True); L.status_add(7,"Left Shoulder Scar","treated fracture",True)
        L.consume_item(9,"glass-lens",1,"Glasshook sight groove","craft")
        L.equipment(11,"char-elian","main_hand","Glasshook","cracked Glass Lens refined into Hooked Shortblade")
        L.consume_item(13,"iron-seal",1,"Anchorfork load spine","craft"); L.consume_item(13,"chainspool",1,"Anchorfork load spine","craft")
        L.equipment(14,"char-mira","main_hand","Anchorfork Spear","bent spear reforged with Iron Seal and Chainspool")
        L.resource(16,"qi",-20,"premature Breath Channel attempt"); L.status_add(17,"Breath Deviation","unsatisfied cultivation gate")
        L.consume_item(19,"cinder-carapace",3,"Verdigris Filter housings","craft"); L.consume_item(19,"acid-gland",2,"Verdigris Filter medium","craft")
        L.gain_item(19,"verdigris-filter","Verdigris Filter",3,"Tempered",1,"Orin refinement")
        L.gain_item(20,"shell-dust","Inert Shell Dust",1,"Common",1,"filter byproduct")
        L.quest(2,"inventory-of-ash","ACCEPTED","finite repair choice"); L.xp(22,60,"Inventory of Ash completion"); L.quest(22,"inventory-of-ash","COMPLETED","two party loadouts restored")
        L.faction(22,"Free Delvers",8,"shared repair and route commitment"); L.trust(22,8,"resource decisions made aloud")
        L.irreversible(21,"final Iron Seal, Chainspool, Glass Lens, carapaces, and acid glands consumed into loadout","refinement")
    elif ch == 6:
        L.resource(2,"qi",20,"Verdigris approach rest"); L.consume_item(3,"verdigris-filter",2,"Sump entry exposure")
        L.quest(2,"keep-the-pump-heart","ACCEPTED","Free Delvers remote contract")
        L.resource(8,"hp",-18,"Mire Choir acid lane"); L.resource(10,"qi",-10,"Fault Hook I"); L.resource(11,"hp",12,"Suture Pulse II")
        L.resource(14,"qi",-8,"Fault Step I fifth verified use")
        L.skill(15,"fault-step","Fault Step",2,10,7,"one linked pivot at verified fault","five verified uses plus Verdigris pressure")
        L.resource(16,"qi",-10,"Fault Step II")
        mira=L.state["party"]["char-mira"]; mira["skills"]["rampart-thrust"]=3; mira["skills"]["bastion-arc"]=1
        L.add(17,"party_skill_change",entity_id="char-mira",changes={"rampart-thrust":{"from":2,"to":3},"bastion-arc":{"from":None,"to":1}},provenance="pump-heart anchored flow")
        L.xp(21,45,"Mire Choir kill share"); L.spend_point(21,"force",1,"Level 5 point allocation"); L.spend_point(21,"guard",1,"Level 6 point allocation")
        L.xp(24,50,"pump-heart quest advancement"); L.quest(24,"keep-the-pump-heart","ADVANCED","heart intact; lower sluice unresolved")
        L.gain_item(22,"sumpglass-coil","Sumpglass Coil",1,"Rare",2,"pump-heart reward"); L.gain_item(22,"pump-token","Pump Token",1,"Rare",0,"Free Delvers proof")
        L.faction(24,"Free Delvers",10,"upper pump restored"); L.trust(24,6,"first three-person combo")
    elif ch == 7:
        L.resource(2,"qi",42,"pump alcove rest")
        L.quest(2,"observe-three-catastrophes","ADVANCED","Belljaw and Bailiff patterns recorded")
        L.resource(10,"hp",-20,"ceiling slab edge"); L.resource(10,"qi",-12,"Fault Sight I"); L.resource(12,"qi",-16,"Rift Draw I aborted after cost")
        L.state["party"]["char-orin"]["equipment"]["utility"]=None
        L.add(10,"equipment_loss",entity_id="char-orin",slot="utility",item="Kiln Satchel",provenance="thrown clear then dissolved in acid water")
        L.resource(14,"qi",-24,"Breath Channel I protection gate")
        L.cultivation(14,"Breath Channel I",12,12,"ceiling diversion protecting Mira and pump heart")
        L.status_remove(14,"Breath Deviation","valid Channel I breakthrough")
        L.quest(15,"observe-three-catastrophes","COMPLETED","Collapse Hound pattern and protection choice")
        L.class_change(16,"Rift Temperer","three catastrophic patterns plus changed protection decision")
        L.skill(16,"rift-mark","Rift Mark",1,22,45,"temporary nonliving fault after survived hostile pattern","Rift Temperer evolution")
        L.xp(20,80,"Collapse Hound kill share"); L.xp(21,60,"Keep the Pump Heart completion")
        L.quest(21,"keep-the-pump-heart","COMPLETED_WITH_LOSS","heart saved; secondary sluice destroyed")
        L.gain_item(22,"rift-nail","Rift Nail",1,"Relic",2,"Collapse Hound counterweight")
        L.gain_item(22,"survey-bracer","Survey Bracer",1,"Tempered",1,"Collapse Hound cache"); L.equipment(22,"char-elian","utility","Survey Bracer","equipped from Hound cache")
        L.resource(23,"hp",12,"Orin field Suture Pulse reserve")
        L.faction(24,"Free Delvers",5,"pump quest completed with heart intact"); L.trust(24,7,"Elian chose protection line")
        L.state["boss_credit"].append("Collapse Hound"); L.state["dungeon"]["cleared"].append("Verdigris Sump")
        L.irreversible(21,"secondary Verdigris sluice destroyed; pump heart survives","completion with loss")
    elif ch == 8:
        L.resource(2,"qi",52,"cistern approach rest")
        L.state["party"]["char-sable"]["ash_debt"]=6
        L.quest(4,"rescue-the-debtor","OPTIONAL_ACCEPTED","Elian accepted with no XP reward")
        L.quest(5,"the-guilds-short-cut","ADVANCED","Ash Crown agents exposed")
        L.gain_item(5,"surface-route-token","Surface-Route Token",1,"Rare",0,"party route credential")
        L.consume_item(5,"surface-route-token",1,"stolen by Ash Crown agents","lost")
        L.irreversible(6,"Surface-Route Token stolen; return door sealed","Ash Crown theft")
        L.resource(9,"qi",-12,"Fault Sight I"); L.state["party"]["char-sable"]["ash_debt"]=7
        L.add(10,"party_status",entity_id="char-sable",status="Ash Debt Default",before_stacks=6,after_stacks=7,provenance="unsupported Severing Lane")
        L.resource(13,"qi",-22,"Rift Mark I"); L.resource(15,"hp",-25,"Brass Maw reversed high note")
        L.consume_item(18,"verdigris-filter",1,"cross Brass Maw acid mist")
        L.resource(20,"qi",-16,"Rift Draw I")
        L.xp(12,40,"Brass Maw full-pattern discovery"); L.xp(21,120,"Brass Maw boss kill share"); L.xp(24,50,"Rescue the Debtor completion")
        L.skill(22,"rift-draw","Rift Draw",2,18,26,"carry through one resonant joint","Brass Maw survived resonance")
        L.gain_item(23,"brass-maw-core","Brass Maw Core",1,"Relic",3,"Brass Maw boss drop"); L.gain_item(23,"tuning-fork-key","Tuning-Fork Key",1,"Rare",1,"Brass Maw boss drop")
        L.item_condition(15,"survey-bracer","cracked","Brass Maw note impact")
        L.quest(24,"rescue-the-debtor","COMPLETED","Sable rejected final debt activation and survived")
        L.state["party"]["char-sable"]["ash_debt"]=5; L.state["party"]["char-sable"]["party_status"]="provisional ally"
        L.add(24,"party_status",entity_id="char-sable",status="stabilized debt",before_stacks=7,after_stacks=5,provenance="Brass Maw resonance vent plus voluntary restraint")
        L.faction(24,"Free Delvers",5,"Sable rescued and cistern cleared"); L.faction(24,"Ash Crown",-15,"defied retrieval order"); L.trust(24,5,"Sable chose brace over debt skill")
        L.spend_point(24,"step",1,"Level 7 point allocation")
        L.state["boss_credit"].append("Brass Maw"); L.state["dungeon"]["cleared"].append("Resonance Cistern")
    elif ch == 9:
        L.resource(2,"hp",17,"three-hour protected forge rest"); L.resource(2,"qi",54,"three-hour protected forge rest")
        L.consume_item(3,"shell-dust",1,"free final loadout slot","discard")
        L.gain_item(4,"crownshaft-wire","Crownshaft Wire",2,"Common",1,"abandoned forge stock")
        L.consume_item(5,"rift-nail",1,"Regentbreaker forge","craft"); L.consume_item(5,"brass-maw-core",1,"Regentbreaker forge","craft")
        L.equipment(5,"char-elian","main_hand","Regentbreaker Edge","Glasshook reforged with Rift Nail and Brass Maw Core")
        L.consume_item(6,"sumpglass-coil",1,"Crownfork tuning","craft"); L.consume_item(6,"tuning-fork-key",1,"Crownfork tuning","craft")
        L.equipment(6,"char-mira","main_hand","Crownfork Spear","Anchorfork tuned with Sumpglass Coil and Tuning-Fork Key")
        L.consume_item(7,"crownshaft-wire",2,"repair Survey Bracer and rebuild Kiln Satchel","craft")
        L.item_condition(7,"survey-bracer","repaired","Crownshaft Wire repair")
        L.state["party"]["char-orin"]["equipment"]["utility"]="Compact Kiln Satchel"
        L.add(7,"equipment_change",entity_id="char-orin",slot="utility",before=None,after="Compact Kiln Satchel",provenance="Crownshaft Wire rebuild")
        L.quest(8,"crownshaft-assault","ACCEPTED","reach Regent chamber and preserve public lift")
        L.skill(12,"fault-sight","Fault Sight",2,14,18,"two linked verified faults for eight seconds","ten verified reads")
        L.resource(12,"qi",-14,"Fault Sight II"); L.resource(14,"qi",-10,"Fault Step II"); L.resource(18,"qi",-22,"Rift Mark I"); L.resource(19,"qi",-18,"Rift Draw II")
        L.state["party"]["char-mira"]["injuries"].append("Left Upper Arm Cut")
        L.add(15,"party_injury",entity_id="char-mira",injury="Left Upper Arm Cut",provenance="Crown Guard blade")
        L.xp(21,90,"Crown Guard kill share"); L.xp(22,40,"Crownshaft ascent objective")
        L.quest(22,"crownshaft-assault","ADVANCED","Regent chamber reached")
        L.quest(24,"strike-the-silence","ACCEPTED","Bell Regent awakened before public lift evacuation")
        L.faction(21,"Free Delvers",6,"Crownshaft ascent broadcast"); L.trust(21,4,"four-person Crosslock")
        L.irreversible(7,"Glasshook, Rift Nail, Brass Maw Core, Anchorfork, Sumpglass Coil, and Tuning-Fork Key consumed into final Relic loadout","Crownshaft forge")
    elif ch == 10:
        L.resource(5,"qi",24,"captured first hostile note")
        L.resource(10,"qi",-14,"Fault Sight II")
        L.xp(11,35,"Crown Guard kill share")
        L.resource(14,"hp",12,"Suture Pulse II from rebuilt satchel")
        L.resource(15,"qi",-22,"Rift Mark I")
        L.resource(16,"hp",-32,"Regent platform stamp")
        L.cultivation(18,"Breath Channel II",10,46,"accepted hostile Bell Regent cadence without surrendering own rhythm")
        L.skill(19,"rift-draw","Rift Draw",3,22,24,"two-stage draw through linked resonance","Breath Channel II plus Bell Regent yoke pattern")
        L.resource(20,"qi",-10,"Fault Step II"); L.resource(22,"qi",-22,"Rift Draw III")
        L.xp(23,180,"Bell Regent boss kill share"); L.xp(24,100,"Strike the Silence completion")
        L.spend_point(24,"force",1,"Level 8 point allocation")
        L.gain_item(23,"bell-crown-shard","Bell Crown Shard",1,"Relic",2,"Bell Regent boss drop")
        L.gain_item(23,"meridian-seal","Meridian Seal",1,"Relic",0,"public-lift clear reward")
        L.gain_item(23,"sponsor-writ","Sponsor Writ",1,"Rare",0,"Bell Regent yoke cache")
        L.quest(23,"strike-the-silence","COMPLETED","Bell Regent defeated; public cable intact")
        L.quest(24,"the-guilds-short-cut","COMPLETED","Sponsor Writ exposes planned breach")
        L.quest(24,"crownshaft-assault","COMPLETED","public lift survives")
        L.faction(24,"Free Delvers",20,"public lift saved"); L.faction(24,"Ash Crown",-25,"sponsor conspiracy exposed"); L.trust(24,6,"four-person Regent resolution")
        L.state["boss_credit"].append("Bell Regent"); L.state["dungeon"]["cleared"].append("Crownshaft")
        L.state["dungeon"]["zone"]="Sealed Fourth Meridian threshold"
        L.irreversible(23,"Bell Regent defeated; public lift cable intact","volume climax")
        L.irreversible(24,"fourth meridian unsealed; Sponsor Writ retained","next-volume vector")
    return L.state, L.transactions


def validate_collection(chapters: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    for index, chapter in enumerate(chapters):
        initial, final = chapter["initial"], chapter["final"]
        if index and initial != chapters[index-1]["final"]:
            errors.append(f'{chapter["chapter"]} initial state does not equal prior final state')
        if final["next_threshold"] != THRESHOLDS[final["level"]]:
            errors.append(f'{chapter["chapter"]} threshold mismatch')
        for item_id, row in final["inventory"].items():
            if row["quantity"] < 0:
                errors.append(f'{chapter["chapter"]} negative inventory: {item_id}')
        if len(final["class_history"]) != len(set(final["class_history"])):
            errors.append(f'{chapter["chapter"]} duplicate class history')
        if len(final["cultivation_history"]) != len(set(final["cultivation_history"])):
            errors.append(f'{chapter["chapter"]} duplicate cultivation history')
    final = chapters[-1]["final"]
    required = {
        "level":8,"xp":295,"next_threshold":400,"class":"Rift Temperer","cultivation":"Breath Channel II","party_trust":42,
    }
    for key, value in required.items():
        if final[key] != value:
            errors.append(f"final {key}: expected {value!r}, found {final[key]!r}")
    if final["factions"] != {"Free Delvers":58,"Ash Crown":-35}:
        errors.append(f'final faction state mismatch: {final["factions"]}')
    if final["stats"] != {"force":8,"step":9,"sense":10,"guard":6}:
        errors.append(f'final stat state mismatch: {final["stats"]}')
    if final["unspent_points"] != 0:
        errors.append("unspent points should reconcile to zero")
    if final["qi"] != {"current":14,"max":90} or final["hp"] != {"current":8,"max":83}:
        errors.append(f'final resource state mismatch: HP {final["hp"]}, Qi {final["qi"]}')
    required_skills={"fault-sight":2,"fault-step":2,"fault-hook":1,"rift-draw":3,"rift-mark":1}
    if {k:v["rank"] for k,v in final["skills"].items()} != required_skills:
        errors.append("final skill ranks mismatch")
    for gone in ("spark-talisman","iron-seal","cinder-key","cinder-carapace","chainspool","resin-suture","glass-lens","acid-gland","stitchfire-ampoule","verdigris-filter","shell-dust","sumpglass-coil","rift-nail","brass-maw-core","tuning-fork-key","surface-route-token","crownshaft-wire"):
        if final["inventory"].get(gone,{}).get("quantity",0) != 0:
            errors.append(f"consumed/lost/discarded item remains: {gone}")
    return errors


def main() -> None:
    state = initial_state()
    chapters = []
    for ch in range(1,11):
        initial = copy.deepcopy(state)
        state, transactions = run_chapter(ch, state)
        chapters.append({
            "schema":"SystemStateLedger/2.0", "chapter":f"ch{ch:02d}", "timeline":TIMES[ch],
            "initial":initial, "transactions":transactions, "final":copy.deepcopy(state),
        })
        write_json(VOLUME / "chapters" / f"ch{ch:02d}" / "system-state.json", chapters[-1])
    errors = validate_collection(chapters)
    report = {
        "schema":"SystemStateValidation/2.0", "status":"PASS" if not errors else "FAIL",
        "errors":errors, "chapters":10,
        "level_ups":sum(bool(t.get("level_events")) for ch in chapters for t in ch["transactions"] if t["type"]=="xp_gain"),
        "class_changes":sum(t["type"]=="class_change" for ch in chapters for t in ch["transactions"]),
        "cultivation_advancements":sum(t["type"]=="cultivation_advance" for ch in chapters for t in ch["transactions"]),
        "skill_changes":sum(t["type"]=="skill_change" for ch in chapters for t in ch["transactions"]),
        "final_state":chapters[-1]["final"],
    }
    write_json(VOLUME / "system-state-ledger.json", {"schema":"SystemStateLedgerCollection/2.0","chapters":chapters})
    write_json(VOLUME / "system-state-validation.json", report)
    if errors:
        raise SystemExit("SystemState validation failed:\n- " + "\n- ".join(errors))
    print(json.dumps({k:report[k] for k in ("status","chapters","level_ups","class_changes","cultivation_advancements","skill_changes")},indent=2))


if __name__ == "__main__":
    main()
