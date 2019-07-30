import json, argparse, math, random
import trec_car_y3_conversion
from trec_car_y3_conversion.y3_data import OutlineReader, Page, Paragraph, ParagraphOrigin

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

def find_most_similar_para(key_para, parapair_score_dict, current_ordering):
    parapairs_with_key = [parapair for parapair in parapair_score_dict.keys() if key_para in parapair]
    most_sim_para = ''
    max_sim_score = 0
    for pair in parapairs_with_key:
        if pair.split("_")[1] == key_para:
            p = pair.split("_")[0]
        else:
            p = pair.split("_")[1]
        ordering_ids = [p.para_id for p in current_ordering]
        if p in ordering_ids:
            continue
        if parapair_score_dict[pair] > max_sim_score:
            most_sim_para = p
            max_sim_score = parapair_score_dict[pair]
    return most_sim_para

def produce_ordering(squid, cand_paralist, parapair_score_dict):
    print("Producing ordering for "+squid)
    ordering = []
    seed_para = cand_paralist[0]
    ordering.append(Paragraph(seed_para))
    key_para = seed_para
    for i in range(1, len(cand_paralist)):
        nearest_para = find_most_similar_para(key_para, parapair_score_dict, ordering)
        ordering.append(Paragraph(nearest_para))
        key_para = nearest_para
    return ordering

def obtain_para_origin(run_dict, squid):
    para_origin_data = []
    sec_para_dict = run_dict[squid]
    for sec in sec_para_dict.keys():
        ret_paralist = sec_para_dict[sec]
        for i in range(min(20, len(ret_paralist))):
            para_origin_data.append(ParagraphOrigin(ret_paralist[i][0], squid+"/"+sec, ret_paralist[i][2], ret_paralist[i][1]))
    return para_origin_data

def main():
    parser = argparse.ArgumentParser(description="A simple method to produce para ordering from parapair scores")
    parser.add_argument("-r", "--run", required=True, help="Path to input passage run file")
    parser.add_argument("-ps", "--pair_score", required=True, help="Path to parapair score file")
    parser.add_argument("-pp", "--page_paras", required=True, help="Path to candidate page paras file")
    parser.add_argument("-ol", "--outline", required=True, help="Path to outline file")
    parser.add_argument("-o", "--out", required=True, help="Path to output file")
    args = vars(parser.parse_args())
    run_file = args["run"]
    pair_score_file = args["pair_score"]
    page_paras_file = args["page_paras"]
    outline_file = args["outline"]
    outfile = args["out"]
    run_id = outfile.split("/")[len(outfile.split("/")) - 1]
    if len(run_id) > 15:
        run_id = run_id[:15]

    run_dict = process_input_para_run_file(run_file)
    with open(page_paras_file, 'r') as pp:
        page_paras = json.load(pp)
    with open(pair_score_file, 'r') as ps:
        pair_scores = json.load(ps)
    with open(outline_file, 'rb') as ol:
        page_outlines = OutlineReader.initialize_pages(ol)
    for page in page_outlines:
        page.paragraphs = produce_ordering(page.squid, page_paras[page.squid], pair_scores)
        page.paragraph_origins = obtain_para_origin(run_dict, page.squid)
        page.run_id = run_id

    with open(outfile, 'w') as out:
        for page in page_outlines:
            json.dump(page.to_json(), out)
            out.write("\n")

if __name__ == '__main__':
    main()