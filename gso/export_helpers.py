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