package com.passengerapp

import android.media.MediaPlayer
import com.facebook.react.bridge.ReactApplicationContext
import com.facebook.react.bridge.ReactContextBaseJavaModule
import com.facebook.react.bridge.ReactMethod

class SplashSoundModule(private val reactContext: ReactApplicationContext) :
    ReactContextBaseJavaModule(reactContext) {

    private var mediaPlayer: MediaPlayer? = null

    override fun getName(): String = "SplashSound"

    @ReactMethod
    fun play() {
        try {
            mediaPlayer?.release()
            val resId = reactContext.resources.getIdentifier("splash_whoosh", "raw", reactContext.packageName)
            if (resId != 0) {
                mediaPlayer = MediaPlayer.create(reactContext, resId)?.apply {
                    setVolume(1.0f, 1.0f) // 100% volume
                    setOnCompletionListener { mp ->
                        mp.release()
                        mediaPlayer = null
                    }
                    start()
                }
            }
        } catch (_: Exception) {}
    }

    @ReactMethod
    fun stop() {
        try {
            mediaPlayer?.stop()
            mediaPlayer?.release()
            mediaPlayer = null
        } catch (_: Exception) {}
    }
}

