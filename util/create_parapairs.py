import json, argparse, math, random

def get_parapairs(paras_in_page):
    parapairs = []
    for i in range(len(paras_in_page) - 1):
        for j in range(i+1, len(paras_in_page)):
            parapairs.append(paras_in_page[i]+"_"+paras_in_page[j])
    return parapairs

def produce_parapairs_from_page_paras(page_paras_dict):
    parapairs_dict = dict()
    for page in page_paras_dict.keys():
        parapairs_dict[page] = {"parapairs":get_parapairs(page_paras_dict[page])}
    return parapairs_dict

def main():
    parser = argparse.ArgumentParser(description="It converts page paras dict to page parapairs")
    parser.add_argument("-p", "--page_paras", required=True, help="Path to page paras file")
    parser.add_argument("-o", "--out", required=True, help="Path to output file")
    args = vars(parser.parse_args())
    page_paras_file = args["page_paras"]
    outfile = args["out"]

    with open(page_paras_file, 'r') as pp:
        page_paras = json.load(pp)
    parapairs = produce_parapairs_from_page_paras(page_paras)
    with open(outfile, 'w') as o:
        json.dump(parapairs, o)

if __name__ == '__main__':
    main()