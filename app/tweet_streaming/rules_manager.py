
from app import seek_confirmation
from app.tweet_streaming.job import MyClient


if __name__ == "__main__":

    client = MyClient()

    print("-------------------------")
    print("EXISTING RULES:")
    response = client.get_rules()
    rules = response.data
    for rule in rules:
        print(rule)


    selection = input("Would you like to 'add' or 'remove' rules? ")

    if selection == "add":
        pass # todo
    elif selection == "remove":

        rule_id = input("Please input the id of the rule you would like to delete!")

        matching_rule = [r for r in rules if r.id == rule_id][0]
        print(matching_rule)

        seek_confirmation()

        print("DELETING")
        client.delete_rules([rule_id])
