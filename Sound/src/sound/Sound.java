package sound;

import javax.sound.sampled.AudioFormat;
import javax.sound.sampled.AudioSystem;
import javax.sound.sampled.Clip;
import javax.sound.sampled.DataLine;

import jp.ne.docomo.smt.dev.aitalk.AiTalkTextToSpeech;
import jp.ne.docomo.smt.dev.aitalk.data.AiTalkSsml;
import jp.ne.docomo.smt.dev.common.exception.SdkException;
import jp.ne.docomo.smt.dev.common.exception.ServerException;
import jp.ne.docomo.smt.dev.common.http.AuthApiKey;

public class Sound {

	// ＡＰＩキー
	static final String APIKEY = "4b4874393877384755546a4a7a5a7575306c55576972496d566866304f414755353537756e524538557337";

	public static void main(String[] args) {
		String msg = "ペットボトルのような資源ごみは火曜日になります";
		String person = "seiji";//"nozomi"、"seiji"、"akari"、"anzu"、"hiroshi"、"kaho"、 "koutarou"、"maki"、"nanako"、"osamu"、"sumire"
		if(args.length > 0){
			msg = args[0];
		}
		if(args.length > 1){
			person = args[1];
		}
		playSound(msg, person);
	}

	public static void playSound(String text, String person) {
		// 音声文字列ＳＳＭＬ
		AiTalkSsml ssml;
		// 音声ＰＣＭリニアデータ
		byte[] resultData = null;

		try {
			// APIKEY の設定
			AuthApiKey.initializeAuth(APIKEY);

			// せいじさんの音声で、文字列を、ＳＳＭＬクラスに登録する
			AiTalkTextToSpeech search = new AiTalkTextToSpeech();
			ssml = new AiTalkSsml();
			ssml.startVoice(person);
			ssml.startProsody(0.8f, 1.2f, 1.2f, 1.0f);
			ssml.addText(text);
			ssml.endProsody();
			ssml.endVoice();

			// 要求処理クラスにリクエストデータを渡し、レスポンスデータを取得する
            resultData = search.requestAiTalkSsmlToSound(ssml.makeSsml());
			// 音声出力
            AudioFormat af = new AudioFormat(16000f,16,1,true,true);
            DataLine.Info info = new DataLine.Info (Clip.class, af);
            Clip clip = (Clip)AudioSystem.getLine(info);
            clip.open(af, resultData, 0, resultData.length);
            clip.start();
            Thread.sleep(resultData.length/32);
            clip.close();
		} catch (SdkException ex) {
			ex.printStackTrace();
		} catch (ServerException ex) {
			ex.printStackTrace();
		} catch (Exception ex) {
			ex.printStackTrace();
		}
	}
}
