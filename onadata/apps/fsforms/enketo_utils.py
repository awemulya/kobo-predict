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


def replace_attachmnt_name(attachment_file_name, instance_xml, attachment_file_extension, attachment_alias):
    file_names_to_be_replaced_in_xml = get_attachment_strings_to_be_replace(attachment_file_name, instance_xml,
                                                                           attachment_file_extension)
    if file_names_to_be_replaced_in_xml:
        for file_name_to_be_replaced_in_xml in file_names_to_be_replaced_in_xml:
            instance_xml = instance_xml.replace(file_name_to_be_replaced_in_xml, attachment_alias)
    return instance_xml


#attachments_keys = [k for k in values.keys() if "instance_attachments" in k]
#instance_xml = values['instance']


def clean_xml_for_enketo(attachments_keys, instance_xml):
    return instance_xml
    for attachment_key in attachments_keys:
        attachment = get_attachment(attachment_key)
        attachment_file_name = os.path.splitext(attachment)[0]
        attachment_file_extension = os.path.splitext(attachment)[1]
        if attachment_file_name in instance_xml:
            instance_xml = replace_attachmnt_name(attachment_file_name, instance_xml, attachment_file_extension, attachment)
        else:
            #     attachment file name have changed trim the kobocat aded text from attachment key
            trimmed_file_name = trim_after_last_hyphen(attachment_file_name)
            if trimmed_file_name in instance_xml:
                instance_xml = replace_attachmnt_name(trimmed_file_name, instance_xml, attachment_file_extension, attachment)
    return instance_xml
