package com.example.myapp

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat

class MainActivity : AppCompatActivity() {
    private lateinit var GoToSecondActivity: Button
    private lateinit var GoToThirdActivity: Button
    private lateinit var GoToFourthActivity: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContentView(R.layout.activity_main)

        GoToSecondActivity = findViewById(R.id.button_calc)
        GoToThirdActivity = findViewById(R.id.button_mp3)
        GoToFourthActivity = findViewById(R.id.button_gps)

        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main)) { v, insets ->
            val systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars())
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom)
            insets
        }
    }
    override fun onResume() {
        super.onResume()
        GoToSecondActivity.setOnClickListener({
            val intent = Intent(this, SecondActivity::class.java)
            startActivity(intent)
        });
        GoToThirdActivity.setOnClickListener({
            val intent = Intent(this, ThirdActivity::class.java)
            startActivity(intent)
        });
        GoToFourthActivity.setOnClickListener({
            val intent = Intent(this, ActivityGPS::class.java)
            startActivity(intent)
        });
    }
}