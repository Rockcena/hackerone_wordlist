#!/usr/bin/env python
# coding: utf-8

import requests,json,base64
from termcolor import colored

banner ="""                  _           _                            
                 (_)         | |                           
  _ __  _ __ ___  _  ___  ___| |_ _ __ ___  ___ ___  _ __  
 | '_ \| '__/ _ \| |/ _ \/ __| __| '__/ _ \/ __/ _ \| '_ \ 
 | |_) | | | (_) | |  __/ (__| |_| | |  __/ (_| (_) | | | |
 | .__/|_|  \___/| |\___|\___|\__|_|  \___|\___\___/|_| |_|
 | |            _/ |                                       
 |_|           |__/                                        
 github.com/projectrecon"""

reqHeaders = {"content-type":"application/json","X-Auth-Token":"----","Content-Length":"0"}
reqTemplate = "{\"operationName\":\"HacktivityPageQuery\",\"variables\":{\"querystring\":\"\",\"where\":{\"report\":{\"disclosed_at\":{\"_is_null\":false}}},\"orderBy\":null,\"secureOrderBy\":{\"latest_disclosable_activity_at\":{\"_direction\":\"ASC\"}},\"count\":25,\"maxShownVoters\":10,\"cursor\":\"[B64ENCODEDID]\"},\"query\":\"query HacktivityPageQuery($querystring: String, $orderBy: HacktivityItemOrderInput, $secureOrderBy: FiltersHacktivityItemFilterOrder, $where: FiltersHacktivityItemFilterInput, $count: Int, $cursor: String, $maxShownVoters: Int) {\\n  me {\\n    id\\n    __typename\\n  }\\n  hacktivity_items(first: $count, after: $cursor, query: $querystring, order_by: $orderBy, secure_order_by: $secureOrderBy, where: $where) {\\n    total_count\\n    ...HacktivityList\\n    __typename\\n  }\\n}\\n\\nfragment HacktivityList on HacktivityItemConnection {\\n  total_count\\n  pageInfo {\\n    endCursor\\n    hasNextPage\\n    __typename\\n  }\\n  edges {\\n    node {\\n      ... on HacktivityItemInterface {\\n        id\\n        databaseId: _id\\n        ...HacktivityItem\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment HacktivityItem on HacktivityItemUnion {\\n  type: __typename\\n  ... on HacktivityItemInterface {\\n    id\\n    votes {\\n      total_count\\n      __typename\\n    }\\n    voters: votes(last: $maxShownVoters) {\\n      edges {\\n        node {\\n          id\\n          user {\\n            id\\n            username\\n            __typename\\n          }\\n          __typename\\n        }\\n        __typename\\n      }\\n      __typename\\n    }\\n    upvoted: upvoted_by_current_user\\n    __typename\\n  }\\n  ... on Undisclosed {\\n    id\\n    ...HacktivityItemUndisclosed\\n    __typename\\n  }\\n  ... on Disclosed {\\n    id\\n    ...HacktivityItemDisclosed\\n    __typename\\n  }\\n  ... on HackerPublished {\\n    id\\n    ...HacktivityItemHackerPublished\\n    __typename\\n  }\\n}\\n\\nfragment HacktivityItemUndisclosed on Undisclosed {\\n  id\\n  reporter {\\n    id\\n    username\\n    ...UserLinkWithMiniProfile\\n    __typename\\n  }\\n  team {\\n    handle\\n    name\\n    medium_profile_picture: profile_picture(size: medium)\\n    url\\n    id\\n    ...TeamLinkWithMiniProfile\\n    __typename\\n  }\\n  latest_disclosable_action\\n  latest_disclosable_activity_at\\n  requires_view_privilege\\n  total_awarded_amount\\n  currency\\n  __typename\\n}\\n\\nfragment TeamLinkWithMiniProfile on Team {\\n  id\\n  handle\\n  name\\n  __typename\\n}\\n\\nfragment UserLinkWithMiniProfile on User {\\n  id\\n  username\\n  __typename\\n}\\n\\nfragment HacktivityItemDisclosed on Disclosed {\\n  id\\n  reporter {\\n    id\\n    username\\n    ...UserLinkWithMiniProfile\\n    __typename\\n  }\\n  team {\\n    handle\\n    name\\n    medium_profile_picture: profile_picture(size: medium)\\n    url\\n    id\\n    ...TeamLinkWithMiniProfile\\n    __typename\\n  }\\n  report {\\n    id\\n    title\\n    substate\\n    url\\n    __typename\\n  }\\n  latest_disclosable_action\\n  latest_disclosable_activity_at\\n  total_awarded_amount\\n  severity_rating\\n  currency\\n  __typename\\n}\\n\\nfragment HacktivityItemHackerPublished on HackerPublished {\\n  id\\n  reporter {\\n    id\\n    username\\n    ...UserLinkWithMiniProfile\\n    __typename\\n  }\\n  team {\\n    id\\n    handle\\n    name\\n    medium_profile_picture: profile_picture(size: medium)\\n    url\\n    ...TeamLinkWithMiniProfile\\n    __typename\\n  }\\n  report {\\n    id\\n    url\\n    title\\n    substate\\n    __typename\\n  }\\n  latest_disclosable_activity_at\\n  severity_rating\\n  __typename\\n}\\n\"}"

print(banner)

def getReport(id):
    report = requests.get("https://hackerone.com/reports/{}.json".format(str(id))).text
    f = open("reports/{}.json".format(str(id)),"w+")
    f.write(report)
    f.close()
    print(colored("[+] Got {}.json".format(str(id)),"green"))

for i in range(25,10000,25):
    try:
        print(colored("[*] Trying to get more repots - {}".format(str(i)),"blue"))
        b64encoded_id = base64.b64encode(str(i).encode()).decode("utf-8")
        reqData = reqTemplate.replace("[B64ENCODEDID]",str(b64encoded_id))
        reqHeaders.update({"Content-Length":str(len(reqData))})
        req = requests.post("https://hackerone.com/graphql",data = reqData,headers=reqHeaders)
        edges = json.loads(req.text)["data"]["hacktivity_items"]["edges"]
        for e in edges:
            if e["node"]["__typename"] == "Disclosed":
                getReport(str(e["node"]["databaseId"]))
    except Exception as e:
        print(colored("[-] Error!","red"))
