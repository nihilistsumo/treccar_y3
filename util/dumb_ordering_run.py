import json, argparse, math, random
import trec_car_y3_conversion
from trec_car_y3_conversion.y3_data import OutlineReader, Page, Paragraph, ParagraphOrigin

# cand_paras is a dict with section IDs as keys and sorted list of paras as values
def produce_ordering(squid, cand_sec_para_dict, para_budget=20):
    cand_para_set = set()
    for s in cand_sec_para_dict.keys():
        cand_para_set = cand_para_set.union(set(cand_sec_para_dict[s]))
    ordering = []
    for s in cand_sec_para_dict.keys():
        ret_paras = cand_sec_para_dict[s]
        ordered_paras_to_insert = ret_paras[:math.floor(para_budget / len(cand_sec_para_dict.keys()))]
        for i in range(len(ordered_paras_to_insert)):
            # ordering.append({"para_id":ordered_paras_to_insert[i][0]})
            ordering.append(Paragraph(ordered_paras_to_insert[i][0]))
    rand_para = random.sample(cand_para_set, 1)[0][0]
    while len(ordering) < para_budget:
        if rand_para not in ordering:
            ordering.append(Paragraph(rand_para))
        rand_para = random.sample(cand_para_set, 1)[0][0]
    return ordering

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

def obtain_para_origin(run_dict, squid):
    para_origin_data = []
    sec_para_dict = run_dict[squid]
    for sec in sec_para_dict.keys():
        ret_paralist = sec_para_dict[sec]
        for i in range(min(20, len(ret_paralist))):
            para_origin_data.append(ParagraphOrigin(ret_paralist[i][0], squid+"/"+sec, ret_paralist[i][2], ret_paralist[i][1]))
    return para_origin_data

def main():
    parser = argparse.ArgumentParser(description="A simple and dumb method to produce para ordering from input para run file")
    parser.add_argument("-r", "--run", required=True, help="Path to input passage run file")
    parser.add_argument("-ol", "--outline", required=True, help="Path to outline file")
    parser.add_argument("-b", "--para_budget", type=int, help="Paragraph budget for each page")
    parser.add_argument("-o", "--out", required=True, help="Path to output file")
    args = vars(parser.parse_args())
    input_run_file = args["run"]
    outline_file = args["outline"]
    budget = args["para_budget"]
    outfile = args["out"]
    run_id = outfile.split("/")[len(outfile.split("/")) - 1]
    if len(run_id) > 15:
        run_id = run_id[:15]

    with open(outline_file, 'rb') as ol:
        page_outlines = OutlineReader.initialize_pages(ol)
    run_dict = process_input_para_run_file(input_run_file)

    for page in page_outlines:
        page.paragraphs = produce_ordering(page.squid, run_dict[page.squid], budget)
        page.paragraph_origins = obtain_para_origin(run_dict, page.squid)
        page.run_id = run_id

    with open(outfile, 'w') as out:
        for page in page_outlines:
            json.dump(page.to_json(), out)
            out.write("\n")

if __name__ == '__main__':
    main()