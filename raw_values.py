import os
import re


def get_attachment(key):
    p = re.compile('instance_attachments\[(.*)\]')
    m = p.search(key)
    if m:
        return m.group(1)
    return None


def get_attachment_strings_to_be_replace(attachment_file_name, instance_xml, attachment_file_extension):
    p = re.compile(attachment_file_name+'(.*)' + attachment_file_extension)
    m = p.findall(instance_xml)
    if m:
        return [attachment_file_name + i + attachment_file_extension for i in m]
    return []


def trim_after_last_hyphen(a):
    return "_".join(a.split("_")[:-1])


values = {u'instance_attachments[Screenshot from 2018-04-04 12-54-06_T0uwOcu.png]': 'http://localhost:8001/media/Promisha/attachments/Screenshot%20from%202018-04-04%2012-54-06_T0uwOcu.png', u'instance_attachments[farcry.webp]': 'http://localhost:8001/media/Promisha/attachments/farcry.webp', 'form_id': u'aq6BX3GMavXWWv5NdCcapK', u'instance_attachments[Screenshot from 2018-03-21 08-45-51_aOl5e6q.png]': 'http://localhost:8001/media/Promisha/attachments/Screenshot%20from%202018-03-21%2008-45-51_aOl5e6q.png', 'server_url': u'http://localhost:8001/Promisha', 'instance_id': u'5e5692d1-39eb-4284-859c-b67f1b0814f6', 'instance': u'<aq6BX3GMavXWWv5NdCcapK_qkk70Ya xmlns:jr="http://openrosa.org/javarosa" xmlns:orx="http://openrosa.org/xforms" id="aq6BX3GMavXWWv5NdCcapK" version="7960">\r\n          <formhub>\r\n            <uuid>fa12a6544eed4a84ae548ebfafd4e2d6</uuid>\r\n          </formhub>\r\n          <group_ringbeam_common>\r\n            <date>2018-09-05</date>\r\n            <name_of_data_collector>eee</name_of_data_collector>\r\n            <is_ring_beam_well_leveled_using_stone_and_sand_cement_1_5_mortar_throughout_the_building_>no</is_ring_beam_well_leveled_using_stone_and_sand_cement_1_5_mortar_throughout_the_building_>\r\n            <the_gable_should_be_demolished_upto_bottom_of_ring_beam_level_need_to_check_the_position_of_eaves_and_also_sometime_the_slope_of_rafter_if_it_allows_us_to_cast_6inch_deep_ring_beam_/>\r\n            <check_whether_the_rafter_is_6_higher_than_the_levelled_surface_or_not_if_not_we_need_to_raise_the_rafter_>no</check_whether_the_rafter_is_6_higher_than_the_levelled_surface_or_not_if_not_we_need_to_raise_the_rafter_>\r\n            <for_the_proper_hold_of_cgi_strap_and_rafter_we_sometimes_need_to_add_an_extra_piece_of_7mm_rebar_in_accordance_to_the_rafter_width/>\r\n            <is_there_4_nos_of_12mm_rebar_at_edges_and_2_nos_of_10mm_rebar_at_the_centre_as_longitudinal_reinforcement_with_7mm_rebar_stirrups_on_ring_beam_>no</is_there_4_nos_of_12mm_rebar_at_edges_and_2_nos_of_10mm_rebar_at_the_centre_as_longitudinal_reinforcement_with_7mm_rebar_stirrups_on_ring_beam_>\r\n            <is_there12mm_threaded_rod_spaced_at_2_feet_c_c_>no</is_there12mm_threaded_rod_spaced_at_2_feet_c_c_>\r\n            <the_threaded_rod_to_be_placed_at_the_inner_side_of_the_longitudinal_wall_and_outer_side_of_the_transverse_wall_/>\r\n            <please_upload_photos_depicting_rebar_arrangement/>\r\n            <photo_mandatory_ type="file">Screenshot from 2018-04-30 09-43-32-10_23_17.png</photo_mandatory_>\r\n            <photo type="file">Screenshot from 2018-04-10 14-46-53-10_23_21.png</photo>\r\n            <photo_0 type="file">farcry-10_23_24.webp</photo_0>\r\n            <is_the_concrete_at_least_m20_grade_or_mix_ratio_1_1_5_3_>no</is_the_concrete_at_least_m20_grade_or_mix_ratio_1_1_5_3_>\r\n            <is_the_concrete_cover_maintained_>no</is_the_concrete_cover_maintained_>\r\n            <is_the_concrete_smooth_without_honeycombing_without_any_exposed_rebars_>no</is_the_concrete_smooth_without_honeycombing_without_any_exposed_rebars_>\r\n            <is_the_rebar_high_strength_deformed_bars_with_fy_415mpa_500mpa_with_overlap_lengths_60_>no</is_the_rebar_high_strength_deformed_bars_with_fy_415mpa_500mpa_with_overlap_lengths_60_>\r\n            <Which_Retofit_types_is_being_i>light_weight_retrofit</Which_Retofit_types_is_being_i>\r\n          </group_ringbeam_common>\r\n          <group_ringbeam1>\r\n            <is_there_presence_of_one_12_mm_dia_u_hook_dowel_bar_at_mid_and_2_nos_at_corner_strongback_connecting_ring_beam_/>\r\n            <need_to_predetermine_the_position_of_strongback_and_also_position_of_u_hook_to_connect_with_strong_back_s_reinforcement_/>\r\n            <is_there_a_16mm_dia_threaded_rod_placed_in_the_ringbeam_connecting_wooden_strongback_>no</is_there_a_16mm_dia_threaded_rod_placed_in_the_ringbeam_connecting_wooden_strongback_>\r\n            <need_to_predetermine_the_position_of_threaded_rod_so_that_it_is_aligned_to_the_centre_of_strongback_/>\r\n          </group_ringbeam1>\r\n          <photos_for_ring_beam_inspection type="file">Screenshot from 2018-04-04 12-54-06-10_23_36.png</photos_for_ring_beam_inspection>\r\n          <Photo_1 type="file">Screenshot from 2018-03-21 08-46-09-10_23_39.png</Photo_1>\r\n          <Photo_1_001 type="file">Screenshot from 2018-03-21 08-45-51-10_23_42.png</Photo_1_001>\r\n          <Photo_1_001_001 type="file">Screenshot from 2018-03-21 08-46-09-10_23_46.png</Photo_1_001_001>\r\n          <comments>eeee</comments>\r\n          <start>2018-09-28T10:23:02.544+06:45</start>\r\n          <end>2018-09-28T10:23:02.547+06:45</end>\r\n          <__version__>7960</__version__>\r\n          <meta>\r\n            <instanceID>uuid:d26e7e81-b04c-470e-aae7-d8425b329726</instanceID>\r\n          </meta>\r\n        </aq6BX3GMavXWWv5NdCcapK_qkk70Ya>', u'instance_attachments[Screenshot from 2018-04-10 14-46-53_WabHsLu.png]': 'http://localhost:8001/media/Promisha/attachments/Screenshot%20from%202018-04-10%2014-46-53_WabHsLu.png', u'instance_attachments[Screenshot from 2018-03-21 08-46-09.png]': 'http://localhost:8001/media/Promisha/attachments/Screenshot%20from%202018-03-21%2008-46-09.png', u'instance_attachments[Screenshot from 2018-04-30 09-43-32_ydLWZl8.png]': 'http://localhost:8001/media/Promisha/attachments/Screenshot%20from%202018-04-30%2009-43-32_ydLWZl8.png', 'return_url': 'http://localhost:8001/Promisha/forms/aq6BX3GMavXWWv5NdCcapK/instance#/42126', u'instance_attachments[Screenshot from 2018-03-21 08-46-09_d0ContT.png]': 'http://localhost:8001/media/Promisha/attachments/Screenshot%20from%202018-03-21%2008-46-09_d0ContT.png'}

attachments_keys = [k for k in values.keys() if "instance_attachments" in k]


def replace_attachmnt_name(attachment_file_name, instance_xml, attachment_file_extension, attachment_alias):
    file_names_to_be_replaced_in_xml = get_attachment_strings_to_be_replace(attachment_file_name, instance_xml,
                                                                           attachment_file_extension)
    if file_names_to_be_replaced_in_xml:
        for file_name_to_be_replaced_in_xml in file_names_to_be_replaced_in_xml:
            print("replacing  ", file_name_to_be_replaced_in_xml, attachment_alias)
            instance_xml = instance_xml.replace(file_name_to_be_replaced_in_xml, attachment_alias)
            return instance_xml


instance_xml = values['instance']
for attachment_key in attachments_keys:
    attachment = get_attachment(attachment_key)
    attachment_file_name = os.path.splitext(attachment)[0]
    attachment_file_extension = os.path.splitext(attachment)[1]
    if attachment_file_name in instance_xml:
        instance_xml = replace_attachmnt_name(attachment_file_name, instance_xml, attachment_file_extension, attachment_key)
    else:
        #     attachment file name have changed trim the kobocat aded text from attachment key
        trimmed_file_name = trim_after_last_hyphen(attachment_file_name)
        if trimmed_file_name in instance_xml:
            instance_xml = replace_attachmnt_name(trimmed_file_name, instance_xml, attachment_file_extension, attachment_key)
print(instance_xml)
