# Lettering and Brass Ledger UI bible — v2

## Dialogue modes

- `soft`: compact irregular balloon, ivory `#f6f0e5` at 84% opacity, charcoal 4 px outline, 0.8 em padding, short mouth-directed tail. Default.
- `open`: no shape; ivory semibold text with charcoal outline and soft shadow. Allowed only on a validated low-detail background with a declared exclusion region and measured local separation.
- `butted`: soft balloon clipped cleanly against top or side border to reclaim art area. Text aligns toward the flat edge.
- `linked`: two soft/butted units sharing one speaker and one thought sequence; only the final unit needs a tail.
- `caption`: small borderless charcoal band at 78% opacity, italic internal voice or narrow uppercase location/time copy.
- `distress`: soft balloon with a subtly uneven line and smaller copy; no decorative spikes unless shouting.

At 1024 px panel width, normal dialogue type is 30–36 px and never renders below a 15 CSS px equivalent at the 390 px review width. Dialogue units normally occupy 26–38% of panel width and must not exceed 44% except a documented butted/linked speech. No balloon may cover a face, hand performing the focal action, weapon contact, loot object, cultivation mark, or system consequence.

## Copy and reading order

Copy is sentence case. Bold-italic emphasis is simulated sparingly with weight/color, never entire speeches. Each unit contains 10–28 words by default and one thought. Longer arguments use linked units. Tails terminate 50–65% of the distance toward the speaker's mouth; off-panel speech butts to the border. Tangencies within 12 px of another lettering outline or focal exclusion fail validation.

## Brass Ledger components

- `status`: level, XP bar and numeric fraction, class, cultivation, HP/Qi, points.
- `delta`: before→after state with provenance.
- `skill`: name/rank, active/passive, exact cost, cooldown, duration/condition, source.
- `inventory`: slots, weight, quantities, rarity, condition, equip/consume/discard choice.
- `quest`: state, objective, optional/hidden flags, reward/failure stakes.
- `enemy`: name, level/class, one verified trait or unknown marker.
- `cultivation`: stage, gate, cost, risk, capacity change.
- `reputation`: faction value, tier and cause.
- `loot`: item, rarity, quantity/condition and provenance.
- `comparison`: CH01 versus CH10 state rows.

UI uses charcoal at 80–86% opacity, brass rules, ember only for changed or dangerous state, and ivory body copy. It is narrow, tall, and information-dense. Four meaningful UI moments appear per chapter; repeated status decoration does not count.

## Validation

The compositor measures copy fit, font floor, balloon/UI coverage, focal-region intersection, safe-frame containment, tail target presence, open-dialogue authorization, and local contrast. Hard clipping, ambiguous speaker ownership, focal occlusion, or unreadable phone type is FAIL. A story-readable tangent or slightly generous whitespace may remain WARN.
