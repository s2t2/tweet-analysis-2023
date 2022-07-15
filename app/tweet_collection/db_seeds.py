

from app.tweet_collection.db import CollectionDatabase
from app.tweet_collection.twitterdev import fetch_context_entities, fetch_context_domains

#def list_to_csv(domain_ids):
#    # SQLite doesn't support nested datatypes like lists, so let's do CSV string for now
#    # in future we could make a separate entities_domains table (but let's do what bq does for now)
#    return ",".join(str(domain_ids))

if __name__ == "__main__":

    db = CollectionDatabase()
    print(db.filepath.upper())

    print("---------------------")
    print("FETCHING CONTEXT ENTITIES...")
    entities_df = fetch_context_entities()
    entities_df.drop(columns=["domain_ids"], inplace=True) # use domains_csv string instead
    print(len(entities_df))
    print(entities_df.head())
    entity_records = entities_df.to_dict("records")
    # todo: consider splitting entities table from entities_domains table
    #db.migrate_entities_table(destructive=True)
    db.drop_entities_table()
    db.save_entities(entity_records)


    print("---------------------")
    print("FETCHING CONTEXT DOMAINS...")
    domains_df = fetch_context_domains()
    print(len(domains_df))
    print(domains_df.head())
    domain_records = domains_df.to_dict("records")
    # todo: consider splitting entities table from entities_domains table
    db.drop_domains_table()
    db.save_domains(entity_records)
