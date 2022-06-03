TOKEN = "5323207728:AAGzOc7CZKGr0f-OPfjntqMiGCqdABC_x_E"


def categories_extractor():
    categories = []

    with open("categories.txt", "r", encoding='utf-8') as f:
        for line in f:
            categories.append(line.replace('\n', '').lower())

    return categories