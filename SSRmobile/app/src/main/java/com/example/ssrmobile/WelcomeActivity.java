package com.example.ssrmobile;

import androidx.appcompat.app.AppCompatActivity;

import android.app.Activity;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.os.Handler;
import android.view.View;

import com.baidu.mapapi.SDKInitializer;

import java.util.Objects;

public class WelcomeActivity extends AppCompatActivity implements FetchApi.OnTaskCompleted {
    private final Handler handler=new Handler();
    public static String sessionId;
    public static SharedPreferences mPreferences;

    private final Runnable runnableBasic=new Runnable() {
        @Override
        public void run() {
            Intent basicIntent = new Intent(getApplicationContext(), BasicActivity.class);
            startActivity(basicIntent);
            finish();
        }
    };

    private final Runnable runnableLogin=new Runnable() {
        @Override
        public void run() {
            Intent loginIntent = new Intent(getApplicationContext(), MainActivity.class);
            startActivity(loginIntent);
            finish();
        }
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_welcome);

        SDKInitializer.initialize(getApplicationContext());

        mPreferences=getPreferences(MODE_PRIVATE);
        sessionId=mPreferences.getString("sessionid",null);

        if (sessionId!=null){
            new FetchApi(this,this).execute("get/user/",null,sessionId);
        }else {
            handler.postDelayed(runnableLogin,2000);
        }
    }

    @Override
    public void onTaskCompleted(String status, String type, String cookie, String content) {
        if (Objects.equals(status, "ok")){
            handler.postDelayed(runnableBasic,2000);
        }else{
            sessionId=null;
            handler.postDelayed(runnableLogin,2000);
        }
    }
}