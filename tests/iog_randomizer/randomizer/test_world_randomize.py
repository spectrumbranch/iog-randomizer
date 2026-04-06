import json

from iog_randomizer.randomizer.classes import World
from iog_randomizer.randomizer.models.enums import *
from iog_randomizer.randomizer.models.randomizer_data import RandomizerData


def get_default_randomizer_data() -> RandomizerData:
    return RandomizerData(seed=13371337,
        difficulty=Difficulty.NORMAL,
        goal=Goal.DARK_GAIA,
        logic=Logic.COMPLETABLE,
        statues="4",
        statue_req=StatueReq.GAME_CHOICE,
        start_location=StartLocation.SOUTH_CAPE,
        enemizer=Enemizer.NONE,
        firebird=False,
        ohko=False,
        red_jewel_madness=False,
        allow_glitches=False,
        boss_shuffle=False,
        open_mode=False,
        z3=False,
        coupled_exits=True,
        town_shuffle=False,
        dungeon_shuffle=False,
        overworld_shuffle=False,
        race_mode=False,
        flute=FluteOpt.START,
        sprite=Sprite.WILL,
        orb_rando=False,
        darkrooms=DarkRooms.NONE,
        printlevel=PrintLevel.SILENT,
        break_on_error=False,
        break_on_init=False,
        ingame_debug=False,
        infinite_inventory=False,
        ds_warp=False,
    )

def get_world(settings) -> World:
    return World(settings=settings,
        statues_required=4,
        statues=[2, 3, 1, 5],
        statue_req=0,
        kara=1,
        gem=[1, 5, 9, 11, 18, 24, 38],
        incatile=[10, 5],
        hieroglyphs=[4, 2, 5, 3, 1, 6],
        boss_order=[1, 2, 3, 4, 5, 6, 7]
    )

def test_can_randomize_with_different_settings_twice():
    world = get_world(get_default_randomizer_data())
    assert world.randomize(seed_adj=0, printlevel=PrintLevel.SILENT, break_on_error=True, break_on_init=False)

    changed_settings = get_default_randomizer_data()
    changed_settings.ohko = True
    world_changed = get_world(changed_settings)
    assert world_changed.randomize(seed_adj=0, printlevel=PrintLevel.SILENT, break_on_error=True, break_on_init=False)

def test_can_randomize_with_same_settings_twice():
    world = get_world(get_default_randomizer_data())
    assert world.randomize(seed_adj=0, printlevel=PrintLevel.SILENT, break_on_error=True, break_on_init=False)

    second_world = get_world(get_default_randomizer_data())
    assert second_world.randomize(seed_adj=0, printlevel=PrintLevel.SILENT, break_on_error=True, break_on_init=False)

    assert world == second_world
