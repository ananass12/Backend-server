package com.example.myapp

import android.Manifest.permission.READ_EXTERNAL_STORAGE
import android.Manifest.permission.READ_MEDIA_AUDIO
import android.content.Intent
import android.content.pm.PackageManager
import android.media.MediaPlayer
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.os.Handler
import android.util.Log
import android.widget.Button
import android.widget.SeekBar
import android.widget.Toast
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import java.io.File
import java.io.IOException

class ThirdActivity : AppCompatActivity() {

    private lateinit var mediaPlayer: MediaPlayer
    private lateinit var playButton: Button
    private lateinit var pauseButton: Button
    private lateinit var forwardButton: Button
    private lateinit var backwardButton: Button
    private lateinit var volumeSeekBar: SeekBar
    private lateinit var progressSeekBar: SeekBar
    private lateinit var goToMainActivity: Button
    private lateinit var nextButton: Button
    private lateinit var prevButton: Button

    private var wasPlaying = false
    private var currentTrackIndex = 0
    private lateinit var audioFiles: Array<File>
    private val logTag = "MEDIA_PLAYER_LOG"

    private val handler = Handler()             //механизм для выполнения задач в основном потоке
    private val updateSeekBar = object : Runnable {
        override fun run() {
            if (::mediaPlayer.isInitialized && mediaPlayer.isPlaying) {
                progressSeekBar.progress = mediaPlayer.currentPosition
            }
            handler.postDelayed(this, 1000)
        }
    }

    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            Toast.makeText(this, "Разрешение получено", Toast.LENGTH_SHORT).show()
            loadAudioFiles()
        } else {
            Toast.makeText(
                this,
                "В разрешении отказано - медиаплеер может не работать",
                Toast.LENGTH_LONG
            ).show()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContentView(R.layout.activity_third)

        playButton = findViewById(R.id.button3)
        pauseButton = findViewById(R.id.button2)
        forwardButton = findViewById(R.id.button)
        backwardButton = findViewById(R.id.button4)
        volumeSeekBar = findViewById(R.id.volume)
        progressSeekBar = findViewById(R.id.peremotka)
        goToMainActivity = findViewById(R.id.button_back)
        nextButton = findViewById(R.id.next_button)
        prevButton = findViewById(R.id.prev_button)

        setupButtons()
        checkAndRequestPermissions()

        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main)) { v, insets ->
            val systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars())
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom)
            insets
        }
    }

    private fun setupButtons() {
        playButton.setOnClickListener {
            if (::mediaPlayer.isInitialized) {
                mediaPlayer.start()
                handler.post(updateSeekBar)
            }
        }

        pauseButton.setOnClickListener {
            if (::mediaPlayer.isInitialized) mediaPlayer.pause()
        }

        forwardButton.setOnClickListener {
            if (::mediaPlayer.isInitialized) {
                val newPosition = mediaPlayer.currentPosition + 5000
                mediaPlayer.seekTo(newPosition.coerceAtMost(mediaPlayer.duration))
            }
        }

        backwardButton.setOnClickListener {
            if (::mediaPlayer.isInitialized) {
                val newPosition = mediaPlayer.currentPosition - 5000
                mediaPlayer.seekTo(newPosition.coerceAtLeast(0))
            }
        }

        goToMainActivity.setOnClickListener {
            val intent = Intent(this, MainActivity::class.java)
            startActivity(intent)
        }

        nextButton.setOnClickListener {
            if (audioFiles.isNotEmpty()) {
                currentTrackIndex = (currentTrackIndex + 1) % audioFiles.size
                playCurrentTrack()
            }
        }

        prevButton.setOnClickListener {
            if (audioFiles.isNotEmpty()) {
                currentTrackIndex = (currentTrackIndex - 1).let {
                    if (it < 0) audioFiles.size - 1 else it
                }
                playCurrentTrack()
            }
        }
    }

    private fun checkAndRequestPermissions() {
        val permission = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            READ_MEDIA_AUDIO
        } else {
            READ_EXTERNAL_STORAGE
        }

        when {
            ContextCompat.checkSelfPermission(
                this,
                permission
            ) == PackageManager.PERMISSION_GRANTED -> {
                loadAudioFiles()
            }
            else -> {
                requestPermissionLauncher.launch(permission)
            }
        }
    }

    private fun loadAudioFiles() {
        val musicDir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_MUSIC)  //плучение пути к папке Music на устройстве
        if (musicDir.exists()) {
            audioFiles = musicDir.listFiles { file ->
                file.extension.lowercase() in listOf("mp3", "wav", "ogg", "m4a")
            } ?: emptyArray()

            if (audioFiles.isNotEmpty()) {
                playCurrentTrack()
            } else {
                Toast.makeText(this, "Не найдено аудио файлов", Toast.LENGTH_LONG).show()
            }
        } else {
            Toast.makeText(this, "Папка с музыкой не найдена", Toast.LENGTH_LONG).show()
        }
    }

    private fun playCurrentTrack() {
        if (audioFiles.isEmpty()) return

        try {
            releaseMediaPlayer()

            mediaPlayer = MediaPlayer().apply {
                setDataSource(audioFiles[currentTrackIndex].absolutePath)         //указание пути к аудиофайлу
                prepare()
                setVolume(1f, 1f)

                setOnPreparedListener {
                    progressSeekBar.max = duration
                    playButton.performClick()
                    updateTrackInfo()
                }

                setOnCompletionListener {
                    nextButton.performClick()
                }
            }

            volumeSeekBar.progress = 100
            volumeSeekBar.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
                override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                    val volume = progress / 100f            //преобразуем значение в дробное(0.0 - 1.0)
                    mediaPlayer.setVolume(volume, volume)
                }
                override fun onStartTrackingTouch(seekBar: SeekBar?) {}
                override fun onStopTrackingTouch(seekBar: SeekBar?) {}
            })

            progressSeekBar.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
                override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                    if (fromUser && ::mediaPlayer.isInitialized) {
                        mediaPlayer.seekTo(progress)
                    }
                }
                override fun onStartTrackingTouch(seekBar: SeekBar?) {}
                override fun onStopTrackingTouch(seekBar: SeekBar?) {}
            })

        } catch (e: IOException) {
            Log.e(logTag, "Ошибка в воспроизведении аудио файла", e)
            Toast.makeText(this, "Ошибка в воспроизведении аудио файла", Toast.LENGTH_SHORT).show()
        } catch (e: IllegalArgumentException) {
            Log.e(logTag, "Недопустимый аудио файл", e)
            Toast.makeText(this, "Недопустимый аудио файл", Toast.LENGTH_SHORT).show()
        }
    }

    private fun updateTrackInfo() {
        val currentTrack = audioFiles[currentTrackIndex]
        Toast.makeText(this, "Играет: ${currentTrack.nameWithoutExtension}", Toast.LENGTH_SHORT).show()
    }

    private fun releaseMediaPlayer() {
        if (::mediaPlayer.isInitialized) {
            if (mediaPlayer.isPlaying) {
                mediaPlayer.stop()
            }
            mediaPlayer.release()
        }
        handler.removeCallbacks(updateSeekBar)
    }

    override fun onPause() {
        super.onPause()
        if (::mediaPlayer.isInitialized) {
            wasPlaying = mediaPlayer.isPlaying
            if (wasPlaying) {
                mediaPlayer.pause()
            }
        }
    }

    override fun onResume() {
        super.onResume()
        if (::mediaPlayer.isInitialized && wasPlaying) {
            mediaPlayer.start()
            handler.post(updateSeekBar)
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        releaseMediaPlayer()
    }
}