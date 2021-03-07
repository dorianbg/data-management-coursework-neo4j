from py2neo import Graph

user = "neo4j"
password = "pass123"
## assumes neo4j running locally
graph = Graph("bolt://localhost", auth=(user, password))

prompts = {
    "initial_prompt": """
1) Find the party that won a given constituency i.e. received the highest number of votes.
    -- please input: the constituency you are interested in
2) Find the list of parties that contested a given constituency, in order of decreasing number of votes, plus the votes that each received.
    -- please input: the constituency you are interested in
3) Find the party that won the election i.e. won the most constituencies.
4) Find the list of parties that contested the election, in order of decreasing number of constituencies won, plus the number of constituencies they each won.
5) Find the constituencies where a given party lost its deposit i.e. won less than 5% of the votes cast at that constituency.
    -- please input: name of the party
6) Find all pairs (c,p) such that party p lost its deposit at constituency c.
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
""",

    "constituency_prompt": """
Please provide the name of the constituency you are interested in
""",

    "party_prompt": """
Please provide the name of the party you are interested in
"""
}

queries = {
    1: """
        MATCH  (ukc:Ukconst)-[ukr:Ukresult]->(ukp:Ukparty) 
        WHERE ukc.ukarea = "{}"
        WITH max(ukr.ukvotes) as max_votes
        MATCH  (ukc:Ukconst)-[ukr:Ukresult]->(ukp:Ukparty) 
        WHERE ukr.ukvotes = max_votes
        RETURN ukp.party as winning_party_in_constituency    
    """,
    2: """
        MATCH  (ukc:Ukconst)-[ukr:Ukresult]->(ukp:Ukparty) 
        WHERE ukc.ukarea = "{}"
        RETURN ukp.party as party, ukr.ukvotes as num_votes
        ORDER BY ukr.ukvotes DESC
    """,
    3: """
        MATCH  (ukc:Ukconst)-[ukr:Ukresult]->(ukp:Ukparty) 
        WITH ukc.ukarea as ukarea, max(ukr.ukvotes) as max_votes
        MATCH  (ukc:Ukconst)-[ukr:Ukresult]->(ukp:Ukparty) 
        WHERE ukc.ukarea = ukarea and ukr.ukvotes = max_votes
        WITH ukp.party as party, count(*) as constituencies_won
        RETURN party as winning_party
        ORDER BY constituencies_won DESC
        LIMIT 1
    """,
    5: """
        MATCH  (ukc:Ukconst)-[ukr:Ukresult]->(ukp:Ukparty) 
        WITH ukc.ukarea as ukarea, sum(ukr.ukvotes) as total_votes
        MATCH  (ukc:Ukconst)-[ukr:Ukresult]->(ukp:Ukparty) 
        WHERE ukc.ukarea = ukarea and ukr.ukvotes < 0.05 * total_votes and ukp.party="{}"
        RETURN ukc.ukarea as constituencies_where_party_lost_deposit
        ORDER BY constituencies_where_party_lost_deposit
    """,
    6: """
        MATCH  (ukc:Ukconst)-[ukr:Ukresult]->(ukp:Ukparty) 
        WITH ukc.ukarea as ukarea, sum(ukr.ukvotes) as total_votes
        MATCH  (ukc:Ukconst)-[ukr:Ukresult]->(ukp:Ukparty) 
        WHERE ukc.ukarea = ukarea and ukr.ukvotes < 0.05 * total_votes
        RETURN ukp.party, ukc.ukarea as constituencies_where_party_lost_deposit
        ORDER BY ukp.party, constituencies_where_party_lost_deposit
    """
}

prompts_for_query = {
    1: "constituency_prompt",
    2: "constituency_prompt",
    5: "party_prompt",
}


def execute_query(query):
    prompt = prompts_for_query.get(query, None)
    if prompt is None:
        run_query(queries[query])
    else:
        run_query(queries[query].format(get_additional_input_from_user(prompts[prompts_for_query[query]])))


def run_query(query):
    print(graph.run(query).to_table())


def get_additional_input_from_user(prompt):
    datainput = None
    while datainput is None:
        datainput = validate_str_input(input(prompt))
    print("We will use your input:", datainput, "\n")
    return datainput


def get_query_user_wants():
    query = None
    while not isinstance(query, int) or not query in [1, 2, 3, 4, 5, 6]:
        try:
            print("Please provide an integer in range 1 to 6")
            query = int(input(prompts["initial_prompt"]))
        except Exception as e:
            print("Please provide an integer in range 1 to 6")
    return query


def validate_str_input(input):
    if not isinstance(input, str):
        print("Please enter a correct string")
        return None
    input = input.lstrip(' ').rstrip(' ')
    return input


if __name__ == '__main__':
    execute_query(get_query_user_wants())
