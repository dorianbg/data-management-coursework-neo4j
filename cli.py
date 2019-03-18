from py2neo import Graph

initial_prompt = """
1) Find the party that won a given constituency i.e. received the highest number of votes.
    -- required input: the constituency you are interested in
2) Find the list of parties that contested a given constituency, in order of decreasing number of votes, plus the votes that each received.
    -- required input: the constituency you are interested in
3) Find the party that won the election i.e. won the most constituencies.
4) Find the list of parties that contested the election, in order of decreasing number of constituencies won, plus the number of constituencies they each won.
5) Find the constituencies where a given party lost its deposit i.e. won less than 5% of the votes cast at that constituency.
    -- required input: name of the party
6) Find all pairs (c,p) such that party p lost its deposit at constituency c.
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""

constituency_prompt = """
Please provide the name of the constituency you are interested in
"""

party_prompt = """
Please provide the name of the party you are interested in
"""

user = "neo4j"
password = "pass123"
# driver = GraphDatabase.driver('bolt://localhost', auth=basic_auth(user, password))
graph = Graph("bolt://localhost", auth=(user, password))


def run():
    question = get_input_query()

    if question == 1:
        constituency = get_other_input(constituency_prompt)
        query1(constituency)

    elif question == 2:
        constituency = get_other_input(constituency_prompt)
        query2(constituency)

    elif question == 3:
        query3()

    elif question == 4:
        pass


    elif question == 5:
        party = get_other_input(party_prompt)


    elif input == 6:
        pass


def get_other_input(prompt):
    datainput = None
    while datainput is None:
        datainput = validate_str_input(input(prompt))
    print("We will use your input:", datainput, "\n")
    return datainput


def get_input_query():
    question = None
    while not isinstance(question, int) or not question in [1, 2, 3, 4, 5, 6]:
        try:
            print("Please provide an integer in range 1 to 6")
            question = int(input(initial_prompt))
        except Exception as e:
            print("Please provide an integer in range 1 to 6")
    return question


def validate_str_input(input):
    if not isinstance(input, str):
        print("Please enter a correct string")
        return None
    return input


def query1(constituency):
    res = graph.run("""
        MATCH  (ukc:Ukconst)-[ukr:Ukresult]->(ukp:Ukparty) 
        WHERE ukc.ukarea = "{}"
        WITH max(ukr.ukvotes) as max_votes
        MATCH  (ukc:Ukconst)-[ukr:Ukresult]->(ukp:Ukparty) 
        WHERE ukr.ukvotes = max_votes
        RETURN ukp.party
    """.format(constituency)).to_table()
    print(res)


def query2(constituency):
    res = graph.run("""
        MATCH  (ukc:Ukconst)-[ukr:Ukresult]->(ukp:Ukparty) 
        WHERE ukc.ukarea = "{}"
        RETURN ukp.party, ukr.ukvotes
        ORDER BY ukr.ukvotes DESC
    """.format(constituency)).to_table()
    print(res)


def query3():
    res = graph.run("""
        MATCH  (ukc:Ukconst)-[ukr:Ukresult]->(ukp:Ukparty) 
        WITH ukc.ukarea as ukarea, max(ukr.ukvotes) as max_votes
        MATCH  (ukc:Ukconst)-[ukr:Ukresult]->(ukp:Ukparty) 
        WHERE ukc.ukarea = ukarea and ukr.ukvotes = max_votes
        WITH ukp.party as party, count(*) as constituencies_won
        RETURN party, constituencies_won
        ORDER BY constituencies_won DESC
        LIMIT 1
    """).to_table()
    print(res)


def query4():
    pass


def query5(party):
    pass


def query6():
    pass


if __name__ == '__main__':
    run()
