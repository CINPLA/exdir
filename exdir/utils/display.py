import pathlib
import exdir

def _build_tree(o):
    contents = "<li>"
    if isinstance(o, exdir.core.File):
        name = o.root_directory.name
    else:
        name = o.object_name

    contents += "{} ({})".format(name, o.__class__.__name__)
    if isinstance(o, exdir.core.Dataset):
        contents += "<ul><li>Shape: {}</li><li>Type: {}</li></ul>".format(o.shape, o.dtype)
    else:
        try:
            keys = o.keys()
            inner_contents = ""
            for a in keys:
                inner_contents += _build_tree(o[a])
            if inner_contents != "":
                contents += "<ul>{}</ul>".format(inner_contents)
        except AttributeError:
            pass

    contents += "</li>"

    return contents

def html_tree(obj):
    from IPython.core.display import display, HTML
    import uuid

    ulid=uuid.uuid1()

    style = """
.collapsibleList li{
    list-style-type : none;
    cursor           : auto;
}

li.collapsibleListOpen{
    list-style-type : circle;
    cursor           : pointer;
}

li.collapsibleListClosed{
    list-style-type : disc;
    cursor           : pointer;
}
    """

    script = """
    var node = document.getElementById('{ulid}');
    exdir.CollapsibleLists.applyTo(node);
    """.format(ulid=ulid)

    result = ("<style>{style}</style>"
              "<ul id='{ulid}' class='collapsibleList'>{contents}</ul>"
              "<script>{script}</script>"
              "").format(style=style, ulid=ulid, contents=_build_tree(obj), script=script)

    return result

