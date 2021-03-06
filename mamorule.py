﻿# -*- coding: utf-8 -*-
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

state = {}


IS_MAC = platform.system() == 'Darwin'

def main_logic(inputfile=None):
    global state
    with open("state.json","r") as f:
        state = json.load(f)
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
        subprocess.check_output(["fswebcam", outputpath])
        
    play_sound("shot.wav")
    return outputpath

def recognize_image(imagepath):
    data = {}
    data["docomo"] = 0
    data["person"], data["pretty"], data["tags"], data["item"]= post_clarifai(imagepath)
    #if post_docomo_image(imagepath) != None:
    #    data["item"] = post_docomo_image(imagepath)
    #    data["docomo"] = 1
    #    print data["item"]
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
        res0 = api.tag(image_file, select_classes="bottle,crow,food")
        #print json.dumps(res0, indent=2)
        
        res0_tags = res0.get("results",{})[0].get("result",{}).get("tag",{})
        #res0_classes = res0_tags.get("classes")
        bottle_probs = res0_tags.get("probs")[0]
        crow_probs = res0_tags.get("probs")[1]
        food_probs = res0_tags.get("probs")[2]
        #print "food_probs"
        #print food_probs
        #if "bird" in res0_classes or "bottle" in res0_classes:
        if (bottle_probs > 0.15):  
            print "bottle"
            return False, "pretty" in res0_classes, res0_classes, u"おーいお茶"
        elif (crow_probs > 0.15):
            print "crow"
            return False, "pretty" in res0_classes, res0_classes, None
        elif (food_probs > 0.3):
            print "food"
            return False, "pretty" in res0_classes, res0_classes, u"チョコパイ"
        res1 = api.tag(image_file, select_classes="pretty,smile")
        print json.dumps(res1, indent=2)
        res1_tags = res1.get("results",{})[0].get("result",{}).get("tag",{})
        res1_classes = res1_tags.get("classes")
        # TODO pretty thre
        pretty_val = res1_tags.get("probs")[0]
	smile_val = res1_tags.get("probs")[1]
        print "PRETTY VAL=%s" % pretty_val
        
        #data["person"], data["pretty"], data["tags"], data["item"]
        return True, pretty_val>0.5, res0_classes, None

def decide_reaction(data):
    person = data.get("person")
    pretty = data.get("pretty")
    tags = data.get("tags", [])
    item = data.get("item")
    docomo = data.get("docomo")
    
    msg = None
    snd = None
    voice = "nozomi" #"nozomi"、"seiji"、"akari"、"anzu"、"hiroshi"、"kaho"、 "koutarou"、"maki"、"nanako"、"osamu"、"sumire"
    print "item is hie"
    print item
    if item:
        #商品として検知されたらゴミ
        if (docomo == 0):
            brand = item
        else:
            brand = item.get("detail", {}).get("brand")
        if u"おーいお茶" in item:
            # bottle == 資源ごみ
            shohin = brand if brand else u"おーいお茶"
            if state.get("pretty", False):
                msg = u"%sは美味しいですよね。本当は火曜日なんだけど、えぇっと、かわいいからOKです" % shohin
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
	msg = None
        #それ以外はアニマル
        if "bird" in tags:
            #からす
            snd = "Crow2.wav"
        elif "cat" in tags:
            snd = "Crow_many.wav"
        else:
            snd = "Cannon.wav"
        
    if smile_val > 0.5:
	if msg != None:
		msg = msg + u“今日も笑顔で頑張りましょう。”

    return msg, voice, snd

def play_message(msg, voice):
    try:
        from slacker import Slacker
        api = Slacker('xoxb-47968952148-lNeZ2FcwqBcdfB5KpBvvzuQO')
        api.chat.post_message("#general", u"%s ;;ue ;;red" % msg, username="Mamorule", as_user=True)
    except:
        print "slack error"
        
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

