# This analyzes the glyphs in parallell using your max number of cpus, I am assumning you already generated all the bmp's with genunicode.py
# Eduardo Ruiz Duarte
# toorandom@gmail.com
from sewar.full_ref import mse, rmse, psnr, uqi, ssim, ergas, scc, rase, sam, msssim, vifp
from math import ceil
from cv2 import imread 
import sys
from multiprocessing import Pool, cpu_count 
from multiprocessing.pool import ThreadPool

# These are the unicode letters allowed in a DNS domain name (TLD) , each bitmap has the filename of its unicode representing letter
allowed_glyphs_files =  ['0030.bmp', '0031.bmp', '0032.bmp', '0033.bmp', '0034.bmp', '0035.bmp', '0036.bmp', '0037.bmp', '0038.bmp', '0039.bmp', '0041.bmp', '0042.bmp', '0043.bmp', '0044.bmp', '0045.bmp', '0046.bmp', '0047.bmp', '0048.bmp', '0049.bmp', '004a.bmp', '004b.bmp', '004c.bmp', '004d.bmp', '004e.bmp', '004f.bmp', '0050.bmp', '0051.bmp', '0052.bmp', '0053.bmp', '0054.bmp', '0055.bmp', '0056.bmp', '0057.bmp', '0058.bmp', '0059.bmp', '005a.bmp', '0061.bmp', '0062.bmp', '0063.bmp', '0064.bmp', '0065.bmp', '0066.bmp', '0067.bmp', '0068.bmp', '0069.bmp', '006a.bmp', '006b.bmp', '006c.bmp', '006d.bmp', '006e.bmp', '006f.bmp', '0070.bmp', '0071.bmp', '0072.bmp', '0073.bmp', '0074.bmp', '0075.bmp', '0076.bmp', '0077.bmp', '0078.bmp', '0079.bmp', '007a.bmp']
allowed_glyphs = {}
uc_glyphs = {} 

# This are the image correlation algorithms that we will consider 
algorithms = [ (msssim,max), (mse,min), (uqi,max), (psnr,max), (vifp,max), (ergas,min) , (scc,max) , (sam,min), (rase,min) ] 
cpus=cpu_count() 
load_perc = 0 
# This function finds the allowed letter (e.g. a,b,c,d...,A,B,C, ..., 0,1,2 .. ) that is more alike an unicode
# glyph which we call weird glyph using 'correlator' which is an algorithm , and a function to find the min or max (extrema) 

def spatial_correlate_ascii(correlator, extrema, weird_glyph): 
    global allowed_glyphs, allowed_glyphs_files 
    correlations = {}
    for allowed_glyph in allowed_glyphs_files:
        allowed_glyph_im = allowed_glyphs[allowed_glyph] 
        correlations[allowed_glyph] = correlator(allowed_glyph_im, uc_glyphs[weird_glyph] ).real
        del allowed_glyph_im
    max_corr_glyph = extrema(correlations,key=correlations.get)
    max_corr = correlations[max_corr_glyph]
    return [ [chr(int(max_corr_glyph[0:4],16)) , str(max_corr) ], correlator.__name__ ]

def load_glyphs(lower_index, upper_index):
    global load_perc, uc_glyphs
    r = range(lower_index, upper_index) 
    for g in r:
        weird_glyph_file =hex(g)[2:].zfill(4)+".bmp"
        uc_glyphs[weird_glyph_file] = imread(weird_glyph_file)
    load_perc=load_perc + round((1/cpus)*100.0 ,1)   
    sys.stderr.write("Loading glyphs " + str(load_perc) + "%\r" ) 



# We initialize the index of rewards, weights and counter
rewards = [0,0,0,0,0,0,0,0,0]
w = [0,0,0,0,0,0,0,0,0]
v = 1


# We load the glyphs into memory in a uniprocessor way (only 36) 
sys.stderr.write("Loading allowed glyphs into memory...\n ")
for fn in allowed_glyphs_files:
    allowed_glyphs[fn] = imread(fn) 

# Creating pool of processes 
# sys.stderr.write("\nBeginning analysis... initializing cpu process pool for multiproc\n")
# pool = Pool(processes=cpu_count() ) 
# 

sys.stderr.write("Loading all unicode glyphs into memory (this can take a while) ...\n ")
load_glyphs_parallel_args= [ (int(65536/cpus*i), int(65536/cpus*(i+1))) for i in range(0,cpus) ]
pool_glyphs = ThreadPool(processes=cpu_count() ) 
pool_glyphs.starmap(load_glyphs,load_glyphs_parallel_args) 

sys.stderr.write("\nInitializing CPU process pool, this takes 30-40 seconds in my lap since fork() is duplicating all the main() memory with all glyphs for each CPU core\n")
pool = Pool(processes=cpu_count() ) 
sys.stderr.write("Done, starting analysis\n");

# We start to analyze each glyph against the allowed glyphs in parallel and storing each algorithm result 
# in an array which includes the predicted allowed letter similar to weird_glyph_im 
for g in range(0x0100,65535):
    weird_glyph_file =hex(g)[2:].zfill(4)+".bmp"
    weird_glyph_im = uc_glyphs[weird_glyph_file] 
    args = [ x + (weird_glyph_file,)  for x in algorithms ] 
    results = pool.starmap(spatial_correlate_ascii,args) 
    similars_all = { z[1]:z[0] for z in results } 
    similars_0 = similars_all['msssim'] 
    similars_1 = similars_all['mse'] 
    similars_2 = similars_all['uqi']
    similars_3 = similars_all['psnr'] 
    similars_4 = similars_all['vifp'] 
    similars_5 = similars_all['ergas'] 
    similars_6 = similars_all['scc'] 
    similars_7 = similars_all['sam'] 
    similars_8 = similars_all['rase'] 
    if float(similars_0[1]) >= 0.85:
# We make a list of the decisions of each algorithm indexed  
        decisions=[similars_0[0]]+[similars_1[0]] +[similars_2[0]] + [similars_3[0]]  + [similars_4[0]] + [similars_5[0]]+[similars_6[0]]+ [similars_7[0]]+ [similars_8[0]]
# The winner letter by 'unweghted democracy' is saved 
        d = { i:decisions.count(i) for i in decisions}
        unweighted_max_similarity_vote = max(d,key=d.get)

# We give a reward to the algorithm that coincided with the majority of the votes and based on this we generate a new weight for the algorithm
# for future votes based on the ratio of guessed votes in the past
        for j in range(0,len(decisions)): 
            if(unweighted_max_similarity_vote in decisions[j]):
                rewards[j] = rewards[j]+1
                w[j] = int(ceil(float(rewards[j])*100.0/float(v)))
# We now generate the weighted decisions index where each vote will appear more times according to the weights and calculate the new winner by 'weighted democracy'
        w_decisions =w[0]*decisions[0]+w[1]*decisions[1] + w[2]*decisions[2] + w[3]*decisions[3]+ w[4]*decisions[4]+ w[5]*decisions[5]+ w[6]*decisions[6]+ w[7]*decisions[7]+ w[8]*decisions[8]
        w_d = { i:w_decisions.count(i) for i in w_decisions}
        max_similarity_vote = max(w_d,key=w_d.get)

        votes = w_d[max(w_d,key=w_d.get)] 

        v=v+1

# If Multi Scale Structural Similarity metric retuned a maximum correlated to >85% then we assume it is
# "alike" some latin character and we print it

    if float(similars_0[1]) >= 0.85:
        print ( weird_glyph_file[0:4]+":"+chr(int(weird_glyph_file[0:4],16))  + " ~ "+ str(max_similarity_vote) + " by algorithm democracy  " + str(list(zip([a[0].__name__ for a in algorithms],w,rewards,decisions))) +" confidence="+ str(round(float(votes*100/len(w_decisions)),2))+"%"   )
