from netrunner.netrunnerdb.decklist import Decklist
from netrunner.alwaysberunning.alwaysberunning import AlwaysBeRunning

a = AlwaysBeRunning()
for result in a.results():
    if result.id == 4086:
        for entry in sorted(result.entries(), key=lambda x: x.rank_swiss):
            if entry.user_name is not None:
                print(f"{entry.rank_swiss}: {entry.user_name} ({entry.user_id})")
                if entry.runner_deck_url is not None:
                    print(Decklist(url=entry.runner_deck_url).cards)
            else:
                print(f"{entry.rank_swiss}")
            print(f"{entry.user_name} ({entry.user_id}): {entry.rank_swiss}")

# decklist = Decklist(id=79610)

# print(decklist.id)
# print(decklist.uuid)
# print(decklist.date_creation)
# print(decklist.date_update)
# print(decklist.name)
# print(decklist.description)
# print(decklist.user_id)
# print(decklist.user_name)
# print(decklist.tournament_badge)
# print(decklist.cards)
# print(decklist.mwl_code)

# decklist2 = Decklist(uuid="4493cfda-8cc3-4498-bff7-d249e039b681")
# decklist3 = Decklist(uuid="b4d11875-27d9-4550-97d2-c99d218970fa")
# print(decklist == decklist2)
# print(decklist != decklist3)