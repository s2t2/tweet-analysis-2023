


# first add a table of 80 domains from here: https://developer.twitter.com/en/docs/twitter-api/annotations/overview





# then add a table of entities from here:
# https://raw.githubusercontent.com/twitterdev/twitter-context-annotations/main/files/evergreen-context-entities-20220601.csv

# each entity has one or more domain_id s
#
# domains,entity_id,entity_name
# ..., ..., ...
# "10,35,131",799022225751871488,Donald Trump
# "10,131",884781076484202496,Donald Trump Jr.



from pandas import read_csv

def domains_list(domains_val) -> list:
    """
    Converts csv_string or int to a list of ints.

    Params domains_val : int like 10 or string like "10,56,131"

    Returns a list of ints.
    """
    return [int(domain_id) for domain_id in str(domains_val).split(",")]

def fetch_context_entities():
    # todo: update the url when a new data file is released
    request_url = "https://raw.githubusercontent.com/twitterdev/twitter-context-annotations/6c349b2f3e1a3e7aca54d941225c485698a93c7a/files/evergreen-context-entities-20220601.csv"
    df = read_csv(request_url)

    # convert csv_string or int to a list of ints:
    df["domain_ids"] = df["domains"].apply(domains_list)
    #df.drop(columns=["domains"], inplace=True)
    df.rename(columns={"domains":"domains_csv"}, inplace=True)

    # clean tab characters and other spaces from the entity names:
    df["entity_name"] = df["entity_name"].apply(lambda txt: txt.strip())

    #df = df.reindex(columns=["domain_ids", "entity_id", "entity_name"])
    return df

def fetch_context_domains():
    # todo: update the url when a new data file is released
    request_url = "https://raw.githubusercontent.com/s2t2/twitter-context-annotations/main/files/evergreen-context-domains-20220601.csv"
    return read_csv(request_url)




if __name__ == "__main__":

    entities_df = fetch_context_entities()
    print(len(entities_df))
    print(entities_df.columns.tolist())
    print(entities_df.head())


    domains_df = fetch_context_domains()
    print(domains_df.head())
    print(len(domains_df))
