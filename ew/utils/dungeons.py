from ew.static import cfg as ewcfg
from ew.static import poi as poi_static
from ew.utils import core as ewutils
from ew.utils import frontend as fe_utils
from ew.utils import rolemgr as ewrolemgr
from ew.utils.combat import EwUser
from ew.cmd.dungeons import dungeonutils
from ..backend import core as bknd_core
from ew.static import hunting as hunt_static

def format_tutorial_response(scene):
    response = scene.text
    if scene.dungeon_state:
        response += "\n\nWhat do you do?\n\n**>options: "
        options = []
        for path in scene.options.keys():
            options.append("{}{}".format(ewcfg.cmd_prefix, path))
        response += ewutils.formatNiceList(names=options, conjunction="or")
        response += "**"

    return response


async def begin_tutorial(member):
    user_data = EwUser(member=member)
    dungeonutils.user_to_tutorial_state[user_data.id_user] = 0

    scene = poi_static.dungeon_tutorial[0]

    if scene.poi != None:
        user_data.poi = scene.poi
    if scene.life_state != None:
        user_data.life_state = scene.life_state

    user_data.persist()

    await ewrolemgr.updateRoles(client=ewutils.get_client(), member=member)

    response = format_tutorial_response(scene)
    poi_def = poi_static.id_to_poi.get(user_data.poi)
    channels = [poi_def.channel]
    return await fe_utils.post_in_channels(member.guild.id, fe_utils.formatMessage(member, response), channels)



def load_npc_blurbs(id_server):
    npcblurbs = bknd_core.execute_sql_query("SELECT {col_id_id_blurb}, {col_id_blurb}, {col_subcontext}, {col_subsubcontext} from blurbs where context = %s and id_server = %s".format(
        col_id_blurb=ewcfg.col_id_blurb,
        col_id_id_blurb=ewcfg.col_id_id_blurb,
        col_subcontext=ewcfg.col_id_subcontext,
        col_subsubcontext=ewcfg.col_id_subsubcontext), ('npc', id_server))

    npc_map = hunt_static.active_npcs_map

    for blurb in npcblurbs:
        npc = npc_map.get(blurb[2])
        if npc is not None:
            current_dialogue_tree = npc.dialogue.get(blurb[3])
            if current_dialogue_tree is None:
                npc.dialogue[blurb[3]] = blurb[1]
