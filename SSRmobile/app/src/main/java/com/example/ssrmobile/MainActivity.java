package com.example.ssrmobile;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextUtils;
import android.text.TextWatcher;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.baidu.mapapi.SDKInitializer;

import org.json.JSONException;
import org.json.JSONObject;

import java.lang.ref.WeakReference;
import java.util.Objects;

import static com.example.ssrmobile.WelcomeActivity.mPreferences;
import static com.example.ssrmobile.WelcomeActivity.sessionId;

public class MainActivity extends AppCompatActivity implements FetchApi.OnTaskCompleted {
    private static final String LOG_TAG = "xhs-json-test";
    private EditText editUsername, editPsw;
    private boolean isUsernameEmpty = true;
    private boolean isPswEmpty = true;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        Button buttonLogin = findViewById(R.id.button_login);
        editUsername = findViewById(R.id.login_edit_username);
        editPsw = findViewById(R.id.login_edit_psw);

        editUsername.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {

            }

            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
                isUsernameEmpty = TextUtils.isEmpty(s);
                buttonLogin.setEnabled(!(isUsernameEmpty || isPswEmpty));
            }

            @Override
            public void afterTextChanged(Editable s) {

            }
        });
        editPsw.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {

            }

            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
                isPswEmpty = TextUtils.isEmpty(s);
                buttonLogin.setEnabled(!(isUsernameEmpty || isPswEmpty));
            }

            @Override
            public void afterTextChanged(Editable s) {

            }
        });
    }

    @Override
    protected void onDestroy() {
//        this.unregisterReceiver(fetchApiReceiver);
        super.onDestroy();
    }

    @Override
    protected void onPause() {
        super.onPause();

        SharedPreferences.Editor preferencesEditor = mPreferences.edit();
        preferencesEditor.putString("sessionid", sessionId);
        preferencesEditor.apply();
    }

    public void onClickRegister(View view) {
        Intent intent = new Intent(this, RegisterActivity.class);
        startActivity(intent);
    }

    public void onClickLogin(View view) {
        JSONObject params = new JSONObject();
        try {
            params.put("username", editUsername.getText())
                    .put("psw", editPsw.getText())
                    .put("auth", "consumer");
        } catch (JSONException e) {
            e.printStackTrace();
        }
        new FetchApi(this, this).execute("login/", params.toString(), sessionId);
        editReset();
    }

    public void onClickReset(View view) {
        editReset();
    }

    private void editReset() {
        editUsername.setText("");
        editPsw.setText("");
    }

    @Override
    public void onTaskCompleted(String status, String type, String cookie, String content) {
        if (Objects.equals(status, "ok")) {
            switch (type){
                case "login":
                    handleLogin(cookie);
                    break;
                default:
            }
        } else {
            String message = status + ", " + type;
            showToast(message);
        }
    }

    private void handleLogin(String cookie) {
        String message = "登录成功！";
        showToast(message);
        sessionId = cookie;
        Intent intent = new Intent(this, BasicActivity.class);
        startActivity(intent);
        finish();
    }

    private void showToast(String toastMessage) {
        Toast.makeText(this, toastMessage, Toast.LENGTH_SHORT).show();
    }
}