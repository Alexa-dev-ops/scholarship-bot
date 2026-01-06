def is_fully_funded(text):
    keywords = [
        "fully funded",
        "full tuition",
        "tuition fees covered",
        "maintenance allowance",
        "living stipend"
    ]
    return any(k in text for k in keywords)


def hidden_funded_phd(text):
    keywords = [
        "ukri",
        "doctoral training partnership",
        "doctoral training centre",
        "dtp",
        "cdt",
        "research council funded"
    ]
    return any(k in text for k in keywords)


def nigeria_eligible(text):
    return (
        "nigeria" in text or
        "all nationalities" in text or
        "international students" in text or
        "africa" in text or
        "commonwealth countries" in text
    )


def degree_ok(text):
    return "master" in text or "phd" in text


def is_eligible(text):
    text = text.lower()
    return (
        degree_ok(text) and
        nigeria_eligible(text) and
        (is_fully_funded(text) or hidden_funded_phd(text))
    )
