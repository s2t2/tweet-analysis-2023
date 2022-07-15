

from app.tweet_collection.bq import BigQueryDatabase
from app.tweet_collection.twitterdev import fetch_context_entities, fetch_context_domains

if __name__ == "__main__":

    db = BigQueryDatabase()

    print("---------------------")
    print("FETCHING CONTEXT ENTITIES...")
    entities_df = fetch_context_entities()
    entities_df.drop(columns=["domains_csv"], inplace=True) # use domain_ids list instead of domains_csv
    print(len(entities_df))
    print(entities_df.head())
    entity_records = entities_df.to_dict("records")
    # todo: consider splitting entities table from entities_domains table
    db.migrate_entities_table(destructive=True)
    db.save_entities(entity_records)


    print("---------------------")
    print("FETCHING CONTEXT DOMAINS...")
    domains_df = fetch_context_domains()
    print(len(domains_df))
    print(domains_df.head())
    domain_records = domains_df.to_dict("records")
    # todo: consider splitting entities table from entities_domains table
    db.migrate_domains_table(destructive=True)
    db.save_domains(domain_records)
