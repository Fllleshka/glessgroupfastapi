def createshortname(firstname, secondname, patroymic) -> str:
    result = firstname + " " + secondname[:1] + "." + patroymic[:1] + "."
    return result