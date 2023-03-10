import os
import time

def get_set_header(base):
    return """USE [{base}]
GO
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

""".replace('{base}', base)

def export_content(base, owner, obj, path, file, text):
    text = [l for l in text.split('\r')]
    save_object(file, text)

def export_sp(base, owner, obj, path, file, text):

    searchtxt = "CREATE PROCEDURE " + obj
    replacetxt = "CREATE PROCEDURE [" + owner + "].[" + obj + "]"

    text = get_set_header(base) + text.replace(searchtxt, replacetxt)
    text = [l for l in text.split('\r')]
    save_object(file, text)

def export_function(base, owner, obj, path, file, text):

    text = get_set_header(base) + text
    text = [l for l in text.split('\r')]
    save_object(file, text)

def export_table(base, owner, obj, path, file, text):

    text = [l for l in text.split('\r')]
    save_object(file, text)

def save_object(file, text):
    with open(file, 'w', encoding='utf-8') as f:
        f.writelines(text)

def was_modified_last_ndays(file_path, ndays=15):
    file_info = os.stat(file_path)
    current_time = time.time()

    dias = (current_time - file_info.st_mtime) / (24 * 60 * 60)
    if current_time - file_info.st_mtime <= ndays * 24 * 60 * 60:
        return True
    else:
        return False
