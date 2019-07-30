import json, argparse, math, random

def process_input_para_run_file(runfile):
    run = dict()
    with open(runfile, 'r') as r:
        for l in r:
            squid = l.split(" ")[0].split("/")[0]
            secid = l.split(" ")[0].split("/")[1]
            paraid = l.split(" ")[2]
            rank = int(l.split(" ")[3])
            score = float(l.split(" ")[4])
            if squid not in run.keys():
                run[squid] = {secid:[(paraid, rank, score)]}
            elif secid not in run[squid].keys():
                run[squid][secid] = [(paraid, rank, score)]
            else:
                run[squid][secid].append((paraid, rank, score))
    return run

######################
# This will produce candidate paras to be reranked as ordering.
# It will be given the sec_para dict of the current page from
# the candidate run file. It will try to take equal number of
# top ranked paras from each section. If resulting cand set exceeds
# budget, it removes the last paras from the list. If the cand
# set has less paras than budget it randomly adds paras from
# any sections to fill the budget.
######################
def produce_cand_paras(squid, cand_sec_para_dict, para_budget=20):
    cand_para_set = set()
    sorted_section_list = list(cand_sec_para_dict.keys())
    sorted_section_list.sort()
    for s in sorted_section_list:
        cand_para_set.update(cand_sec_para_dict[s])
    cand_paras = []
    n = round(para_budget / len(sorted_section_list))
    for s in sorted_section_list:
        ret_paras = cand_sec_para_dict[s]
        # ordered_paras_to_insert = ret_paras[:n]
        i = 0
        add = 0
        while add < n:
            if ret_paras[i][0] not in cand_paras:
                cand_paras.append(ret_paras[i][0])
                add += 1
            i += 1
        # for i in range(len(ordered_paras_to_insert)):
            # cand_paras.append({"para_id":ordered_paras_to_insert[i][0]})
            # cand_paras.append(ordered_paras_to_insert[i][0])
    if len(cand_paras) > para_budget:
        cand_paras = cand_paras[:para_budget]
    else:
        rand_para = random.sample(cand_para_set, 1)[0][0]
        while len(cand_paras) < para_budget:
            if rand_para not in cand_paras:
                cand_paras.append(rand_para)
            rand_para = random.sample(cand_para_set, 1)[0][0]
    return cand_paras

def main():
    parser = argparse.ArgumentParser(description="Produce candidate page paras")
    parser.add_argument("-r", "--run", required=True, help="Path to input passage run file")
    parser.add_argument("-b", "--para_budget", type=int, help="Paragraph budget for each page")
    parser.add_argument("-o", "--out", required=True, help="Path to output file")
    args = vars(parser.parse_args())
    input_run_file = args["run"]
    budget = args["para_budget"]
    outfile = args["out"]

    run_dict = process_input_para_run_file(input_run_file)
    cand_page_paras = dict()
    for page in run_dict.keys():
        cand_page_paras[page] = produce_cand_paras(page, run_dict[page], budget)
    with open(outfile, 'w') as o:
        json.dump(cand_page_paras, o)

if __name__ == '__main__':
    main()