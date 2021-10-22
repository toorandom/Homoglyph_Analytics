# This codes finds for all the generated glyphs the most similar allowed character (DNS allowed char) by calculating a factor of similarity against all 
# and then getting the most similar. This is done by several Image recognition algorithms. Then they will "vote" for their most similar glyph and that will be the outcome
# being MSSSIM the one with the highest weight due to the fact that it performs much better according to a previous analysis
# Run with Python3  AFTER running the genunicodes.py
# Eduardo Ruiz Duarte
# toorandom@gmail.com
#

from sewar.full_ref import mse, rmse, psnr, uqi, ssim, ergas, scc, rase, sam, msssim, vifp
from cv2 import imread 
import sys

allowed_glyphs =  ['0030.bmp', '0031.bmp', '0032.bmp', '0033.bmp', '0034.bmp', '0035.bmp', '0036.bmp', '0037.bmp', '0038.bmp', '0039.bmp', '0041.bmp', '0042.bmp', '0043.bmp', '0044.bmp', '0045.bmp', '0046.bmp', '0047.bmp', '0048.bmp', '0049.bmp', '004a.bmp', '004b.bmp', '004c.bmp', '004d.bmp', '004e.bmp', '004f.bmp', '0050.bmp', '0051.bmp', '0052.bmp', '0053.bmp', '0054.bmp', '0055.bmp', '0056.bmp', '0057.bmp', '0058.bmp', '0059.bmp', '005a.bmp', '0061.bmp', '0062.bmp', '0063.bmp', '0064.bmp', '0065.bmp', '0066.bmp', '0067.bmp', '0068.bmp', '0069.bmp', '006a.bmp', '006b.bmp', '006c.bmp', '006d.bmp', '006e.bmp', '006f.bmp', '0070.bmp', '0071.bmp', '0072.bmp', '0073.bmp', '0074.bmp', '0075.bmp', '0076.bmp', '0077.bmp', '0078.bmp', '0079.bmp', '007a.bmp']

def spatial_correlate_ascii(weird_glyph_im, correlator, extrema):
    correlations = {}
    for allowed_glyph in allowed_glyphs:
        allowed_glyph_im = imread(allowed_glyph)
        correlations[allowed_glyph] = correlator(allowed_glyph_im, weird_glyph_im).real
        del allowed_glyph_im
    max_corr_glyph = extrema(correlations,key=correlations.get)
    max_corr = correlations[max_corr_glyph]
    del correlations[max_corr_glyph]
    second_max_corr_glyph = extrema(correlations,key=correlations.get)
    second_max_corr = correlations[second_max_corr_glyph]
    return [ [chr(int(max_corr_glyph[0:4],16)) , str(max_corr) ], [chr(int(second_max_corr_glyph[0:4],16)) , str(second_max_corr)] ]



for g in range(0x017b,65535):
    weird_glyph_file =hex(g)[2:].zfill(4)+".bmp"
    weird_glyph_im = imread(weird_glyph_file)
#    similars_1 = spatial_correlate_ascii(weird_glyph_im,msssim,max) 
#    similars_2 = spatial_correlate_ascii(weird_glyph_im,mse,min)
#    similars_3 = spatial_correlate_ascii(weird_glyph_im,uqi,max)
    similars_1 = spatial_correlate_ascii(weird_glyph_im,msssim,max)
    similars_2 = spatial_correlate_ascii(weird_glyph_im,mse,min)
    similars_3 = spatial_correlate_ascii(weird_glyph_im,uqi,max)
    similars_4 = spatial_correlate_ascii(weird_glyph_im,psnr,max)
    similars_5 = spatial_correlate_ascii(weird_glyph_im,vifp,max)
    similars_6 = spatial_correlate_ascii(weird_glyph_im,ergas,min)
    similars_7 = spatial_correlate_ascii(weird_glyph_im,scc,max)
    similars_8 = spatial_correlate_ascii(weird_glyph_im,sam,min)
    similars_9 = spatial_correlate_ascii(weird_glyph_im,rase,min)

    #x = 3*[similars_1[0][0]]+2*[similars_1[1][0]]+3*[similars_2[0][0]] + 2*[similars_2[1][0]] + 3*[similars_3[0][0]] + 2*[similars_3[1][0]] + 3*[similars_4[0][0]] + 2*[similars_4[1][0]]   
    x =5*[similars_1[0][0]]+[similars_2[0][0]] + [similars_3[0][0]] + [similars_4[0][0]]  + [similars_5[0][0]] + [similars_6[0][0]]+ [similars_7[0][0]]+ [similars_8[0][0]]+ [similars_9[0][0]]
    d = { i:x.count(i) for i in x}
    max_similarity_vote = max(d,key=d.get)
    votes = d[max(d,key=d.get)] 


    del weird_glyph_im
    if float(similars_1[0][1]) >= 0.85:
        print ( weird_glyph_file[0:4]+":"+chr(int(weird_glyph_file[0:4],16))  + " ~ "+ str(max_similarity_vote) + " by algorithm democracy over votes: " + str(x) +" "+ str(votes)+"/"+str(len(x)) +  ". MSSSIM returned similarity to " + similars_1[0][0] + '->' + similars_1[0][1]  )
