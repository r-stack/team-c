# -*- coding: utf-8 -*-
'''
Created on 2016/07/07

@author: ken
'''
import platform
import subprocess
import json
import sys

from docomocv import DocomoCVClient, Recog
from clarifai.client import ClarifaiApi
from Carbon.AppleEvents import cRow

state = {}


IS_MAC = platform.system() == 'Darwin'

def main_logic(inputfile=None):
    global state
    print "recognize_area"
    with open("state.json","r") as f:
        state = json.load(f)
    print json.dumps(state, indent=2)
    if inputfile:
        imagepath = inputfile
    else:
        imagepath = capture_image("input.jpg")
    
    data = recognize_image(imagepath)
    
    msg, voice, snd = decide_reaction(data)
    
    if msg:
        play_message(msg, voice)
    if snd:
        play_sound(snd)
    
    with open("state.json", "w") as f:
        json.dump(state, f)
    
    
def capture_image(outputpath):    
    """
    
    """
    if IS_MAC:
        subprocess.check_output(["imagesnap",
                                 outputpath,
                                 "-w",
                                 "1.0"])
    else:
        subprocess.check_output(["cat", outputpath])
    return outputpath

def recognize_image(imagepath):
    data = {}
    #data["item"] = post_docomo_image(imagepath)
    
    data["person"], data["pretty"], data["tags"], data["item"]= post_clarifai(imagepath)
    
    return data
    

def post_docomo_image(imagepath):
    print "recognaize syohin(docomo)"
    client = DocomoCVClient("4b4874393877384755546a4a7a5a7575306c55576972496d566866304f414755353537756e524538557337")
    result = client.recognize(imagepath, Recog.food)
    print "docomo API is here"
    print json.dumps(result, indent=2)
    can = result.get("candidates")
    if can and len(can)>0:
        return can[0]
    else:
        return None
#     result = subprocess.check_output(["bash", "docomo_image.sh" ,imagepath])
#     try:
#         return json.loads(result)
#     except:
#         return {}

    
def post_docomo_tts(msg):
    result = subprocess.check_output("")
    
def post_clarifai(imagepath):
    """
    @return person(bool), pretty(bool), tags(list)
    """
    print "START_CLARIFAI"
    app_id = "J-1HVOns4pAe61vumq7NFHvf-TpHXrX54WaKyVyD"
    app_secret = "sY9cM9tyklkhcNv_6gWPs9_ihqv9Amxw5H_1wxiH"
    api = ClarifaiApi(app_id, app_secret)
    with open(imagepath,'rb') as image_file:
        res0 = api.tag(image_file, select_classes="bottle,crow")
        print json.dumps(res0, indent=2)
        
        res0_tags = res0.get("results",{})[0].get("result",{}).get("tag",{})
        res0_classes = res0_tags.get("classes")
        bottle_probs = res0_tags.get("probs")[0]
        crow_probs = res0_tags.get("probs")[1]
       #ship@ofsks
        print "res0_classes"
        print res0_classes
        #if "bird" in res0_classes or "bottle" in res0_classes:
        if (bottle_probs > 0.1):  
            print "bottle"
            return False, "pretty" in res0_classes, res0_classes, "bottle"
        elif (crow_probs > 0.0):
            print "crow"
            return False, "pretty" in res0_classes, res0_classes, "bird" 
        res1 = api.tag(image_file, select_classes="pretty,human,man,woman")
        print json.dumps(res1, indent=2)
        res1_tags = res1.get("results",{})[0].get("result",{}).get("tag",{})
        res1_classes = res1_tags.get("classes")
        # TODO pretty thre
        pretty_val = res1_tags.get("probs")[0]
        print "PRETTY VAL=%s" % pretty_val
        
        #data["person"], data["pretty"], data["tags"], data["item"]
        return True, pretty_val>0.25, res0_classes, None

def decide_reaction(data):
    person = data.get("person")
    pretty = data.get("pretty")
    tags = data.get("tags", [])
    item = data.get("item")
    
    msg = None
    snd = None
    voice = "nozomi" #"nozomi"、"seiji"、"akari"、"anzu"、"hiroshi"、"kaho"、 "koutarou"、"maki"、"nanako"、"osamu"、"sumire"
    print "item is hie"
    print item
    if item:
        #商品として検知されたらゴミ
        brand = item#item.get("detail", {}).get("brand")
        if "bottle" in tags:
            # bottle == 資源ごみ
            shohin = brand if brand else u"おーいお茶"
            if state.get("pretty", False):
                msg = u"本当は火曜日なんだけど、えぇっと、かわいいからOKです"
                voice = 'seiji'
            else:
                msg = u"おはようございます。ペットボトルは火曜日に出すようにしてください。"
                
        else:
            # それ以外は燃えるゴミ
            shohin = brand if brand else u"チョコパイ"
            msg = u"いつも分別にご協力いただきまして、ありがとうございます。%sは美味しいですよね" % shohin
    elif person:
        state["pretty"] = pretty
        msg = u"おはようございます。"
        if pretty:
            voice = "seiji"
    else:
        #それ以外はアニマル
        if "bird" in tags:
            #からす
            snd = "Crow2.wav"
        elif "cat" in tags:
            snd = "Crow_many.wav"
        else:
            snd = "Cannon.wav"
        
    
    return msg, voice, snd

def play_message(msg, voice):
    subprocess.check_output(["bash",
                             "docomo_tts.sh",
                                 msg,
                                 voice])



def play_sound(snd):
    if IS_MAC:
        subprocess.check_output(["afplay",
                                 snd])
    else:
        subprocess.check_output(["aplay",
                                 snd])


if __name__ == '__main__':
    print "main start"
    inputfile = None
    if len(sys.argv) > 1:
        inputfile = sys.argv[1]
    
    main_logic(inputfile)