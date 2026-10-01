import unittest
import xml.etree.ElementTree as ET

from affix_overview.constants import DYNAMIC_BASE_VALUES_PATH, HERO_NAME_OVERRIDES_PATH
from affix_overview.data_loading import load_dynamic_base_values, load_hero_name_overrides
from affix_overview.dynamic_values import DynamicValueResolver
from affix_overview.markup import convert_storm_markup


class DynamicValuesTest(unittest.TestCase):
    def setUp(self):
        self.base_values = load_dynamic_base_values(DYNAMIC_BASE_VALUES_PATH)
        self.resolver = DynamicValueResolver(base_values=self.base_values)
        self.resolver.set_hero_name_overrides(load_hero_name_overrides(HERO_NAME_OVERRIDES_PATH))

    def test_assassin_tooltip_constants_and_hero_reductions(self):
        initial = "libAffx_PathoftheAssassinInitialValueTooltip"
        stacking = "libAffx_PathoftheAssassinStackingValueTooltip"
        self.assertEqual(self.resolver.resolve_ref(f"$GalaxyVar:{initial}$"), 4)
        self.assertEqual(self.resolver.resolve_ref(f"$GalaxyVar:{stacking}$"), 2)
        for name, tracer, fast in ((initial, 1, 2), (stacking, 1, 1)):
            group = self.resolver.resolve_galaxy_var_variants(name)
            variants = {hero: variant.value for variant in group.variants for hero in variant.heroes}
            self.assertEqual(variants, {
                "Tracer": tracer, "DVa": fast, "Tassadar": fast, "Tychus": fast,
                "Zarya": fast, "Lucio": fast, "Genji": fast,
            })
        rendered, plain, footnotes = convert_storm_markup(
            f'+<d ref="$GalaxyVar:{initial}$" precision="0"/> '
            f'(+<d ref="$GalaxyVar:{stacking}$" precision="1"/> per stack)',
            self.resolver,
        )
        self.assertEqual(plain, "+4* (+2.0** per stack)")
        self.assertIn("Reduced to 1 for Tracer.", footnotes[0].text)
        self.assertIn("D.Va", footnotes[0].text)
        self.assertIn("Lúcio", footnotes[0].text)
        self.assertNotIn("[dynamic]", rendered)

    def test_array_tooltips_require_complete_constant_hero_branches(self):
        source = '''bool libAffx_Example(bool testConds, bool runActions) {
    hero = libCore_gf_GetHeroFromIndex(libAffx_playersHeroIndex[i]);
    if (hero == "Tracer") {
        bonus[i] = 1;
    } else {
        bonus[i] = base / 2;
    }
    bonusTooltip = bonus[libAffx_player];
}
'''
        values = {"base": 8}
        self.resolver._extract_player_array_tooltips(source, values)
        self.assertEqual(values["bonusTooltip"], 4)
        for invalid in (
            source.replace('hero == "Tracer"', 'hero == "Tracer" && enabled'),
            source.replace('bonus[i] = 1;', 'other[i] = 1;'),
            source.replace('base / 2', 'UnitLevel(unit)'),
            source.replace(
                'if (hero == "Tracer")',
                'if (HasTalent(unit)) { bonus[i] = 10; } else if (hero == "Tracer")',
            ),
        ):
            with self.subTest(source=invalid):
                values = {"base": 8}
                self.resolver._extract_player_array_tooltips(invalid, values)
                self.assertNotIn("bonusTooltip", values)

    def test_uther_base_values_have_visible_notes(self):
        for ref, expected in (
            ("Effect,HolyLightCreateHealer,RechargeVitalRate", 362),
            ("Effect,UtherHolyLightDamage,Amount", 362),
            ("Effect,UtherFlashofLightDamage,Amount", 230),
        ):
            with self.subTest(ref=ref):
                self.assertEqual(self.resolver.resolve_ref(ref), expected)
                rendered, plain, footnotes = convert_storm_markup(f'<d ref="{ref}"/>', self.resolver)
                self.assertEqual(plain, f"{expected}*")
                self.assertIn("Base value before level scaling", footnotes[0].text)
                self.assertIn("dynamic-footnote-marker", rendered)

    def test_identical_base_notes_share_one_footnote(self):
        _, plain, footnotes = convert_storm_markup(
            '<d ref="Effect,UtherHolyLightDamage,Amount"/> / '
            '<d ref="Effect,UtherFlashofLightDamage,Amount"/>',
            self.resolver,
        )
        self.assertEqual(plain, "362* / 230*")
        self.assertEqual(len(footnotes), 1)

    def test_catalog_values_and_manual_overrides_take_precedence(self):
        ref = "Effect,UtherHolyLightDamage,Amount"
        self.resolver.catalog_entries["Effect"]["UtherHolyLightDamage"] = ET.fromstring(
            '<CEffectDamage id="UtherHolyLightDamage"><Amount value="400"/></CEffectDamage>'
        )
        self.assertEqual(self.resolver.resolve_ref(ref), 400)
        self.assertIsNone(self.resolver.resolve_base_value_note(ref))
        self.resolver.manual_overrides[ref] = 500
        self.assertEqual(self.resolver.resolve_ref(ref), 500)
        self.assertIsNone(self.resolver.resolve_base_value_note(ref))

    def test_zero_stack_base_is_explicit_and_unknown_runtime_values_stay_unresolved(self):
        ref = (
            "$BehaviorTokenCount:WitchDoctorVoodooRitual$*"
            "(Accumulator,NazeeboPowerRitualLightningRitualAccumulator,Scale)*100"
        )
        rendered, plain, footnotes = convert_storm_markup(f'<d ref="{ref}" precision="0"/>%', self.resolver)
        self.assertEqual(plain, "0*%")
        self.assertIn("0 Voodoo Ritual stacks", footnotes[0].text)
        self.assertIn("0.3%", footnotes[0].text)
        self.assertNotIn("[dynamic]", rendered)
        self.assertIsNone(self.resolver.resolve_ref("$BehaviorTokenCount:Unknown$"))


if __name__ == "__main__":
    unittest.main()
