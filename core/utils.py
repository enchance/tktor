def split_fullname(fullname: str | None, default: str = '',
                   prefix: str | list | tuple | None = None,
                   suffix: str | list | tuple | None = None) -> tuple:
    """
    Splits a fullname into their respective first_name and last_name fields.
    If only one name is given, that becomes the first_name
    :param fullname:    The name to split
    :param default:     The value if only one name is given
    :param prefix:      Custom prefixes to append to the default list
    :param suffix:      Custom suffixes to append to the default list
    :return:            tuple
    """
    if not fullname:
        return '', ''

    if prefix and not isinstance(prefix, (str, list, tuple)):
        raise TypeError('`prefix` must be a list/str for multi/single values.')

    if suffix and not isinstance(suffix, (str, list, tuple)):
        raise TypeError('`suffix` must be a list/str for multi/single values.')

    prefix = isinstance(prefix, str) and [prefix] or prefix or []
    suffix = isinstance(suffix, str) and [suffix] or suffix or []
    prefix_lastname = ['dos', 'de', 'delos', 'san', 'dela', 'dona', 'van', 'von', 'der', 'de la', 'bin', 'ben', 'al',
                       'Mc', 'O\'', 'Le', 'Mac', 'St.', 'St', 'La', 'L\'', 'L', 'Da', 'D\'', 'D', 'Te', 'Ibn', 'I',
                       *prefix]
    suffix_lastname = ['phd', 'md', 'rn', 'jr', 'sr', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x', 'esq',
                       *suffix]

    list_ = fullname.split()
    lastname_idx = None
    if len(list_) > 2:
        for idx, val in enumerate(list_):
            if val.lower() in prefix_lastname:
                lastname_idx = idx
                break
            elif val.lower().replace('.', '') in suffix_lastname:
                lastname_idx = idx - 1
            else:
                if idx == len(list_) - 1:
                    lastname_idx = idx
                else:
                    continue
        list_[:lastname_idx] = [' '.join(list_[:lastname_idx])]
        list_[1:] = [' '.join(list_[1:])]
    try:
        first, last = list_
    except ValueError:
        first, last = [*list_, default]
    return first, last


def name_extractor(email: str, **kwargs) -> tuple[str, str, str, dict]:
    """
    Try to extract the name of the user from their email.
    :param email:   Account email
    :param kwargs:  Overridden values
    :return:        tuple
    """
    email_user = str(email).split('@')[0]
    firstname = kwargs.pop('firstname', '')
    lastname = kwargs.pop('lastname', '')

    if {'.', '_'} & set(email_user):
        swap = email_user.maketrans({'.': ' ', '_': ' '})
        firstnm, lastnm = split_fullname(email_user.translate(swap))
        firstname = firstname or firstnm
        lastname = lastname or lastnm
    display = kwargs.pop('display', '') or firstname or email_user.lower()

    return firstname, lastname, display, kwargs
