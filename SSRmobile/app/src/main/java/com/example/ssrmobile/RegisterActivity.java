package com.example.ssrmobile;

import android.os.Bundle;
import android.text.Editable;
import android.text.TextUtils;
import android.text.TextWatcher;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import org.json.JSONException;
import org.json.JSONObject;

import java.lang.ref.WeakReference;
import java.util.Objects;

public class RegisterActivity extends AppCompatActivity implements FetchApi.OnTaskCompleted {
    public static WeakReference<RegisterActivity> context;
    private EditText editUsername, editPsw1, editPsw2, editEmail;
    private Button buttonRegister;
    private boolean isUsernameEmpty = true;
    private boolean isPsw1Empty = true;
    private boolean isPsw2Empty = true;
    private boolean isEmailEmpty = true;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_register);

        context = new WeakReference<>(this);

        editUsername = findViewById(R.id.register_edit_username);
        editPsw1 = findViewById(R.id.register_edit_psw1);
        editPsw2 = findViewById(R.id.register_edit_psw2);
        editEmail = findViewById(R.id.register_edit_email);
        buttonRegister = findViewById(R.id.register_button_register);

        buttonRegister.setEnabled(false);

        editUsername.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {

            }

            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
                isUsernameEmpty = TextUtils.isEmpty(s);
                buttonRegister.setEnabled(!(isUsernameEmpty || isEmailEmpty || isPsw1Empty || isPsw2Empty));
            }

            @Override
            public void afterTextChanged(Editable s) {

            }
        });
        editEmail.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {

            }

            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
                isEmailEmpty = TextUtils.isEmpty(s);
                buttonRegister.setEnabled(!(isUsernameEmpty || isEmailEmpty || isPsw1Empty || isPsw2Empty));
            }

            @Override
            public void afterTextChanged(Editable s) {

            }
        });
        editPsw1.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {

            }

            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
                isPsw1Empty = TextUtils.isEmpty(s);
                buttonRegister.setEnabled(!(isUsernameEmpty || isEmailEmpty || isPsw1Empty || isPsw2Empty));
            }

            @Override
            public void afterTextChanged(Editable s) {

            }
        });
        editPsw2.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {

            }

            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
                isPsw2Empty = TextUtils.isEmpty(s);
                buttonRegister.setEnabled(!(isUsernameEmpty || isEmailEmpty || isPsw1Empty || isPsw2Empty));
            }

            @Override
            public void afterTextChanged(Editable s) {

            }
        });
    }

    public void onClickRegister(View view) {
        String psw1 = editPsw1.getText().toString();
        String psw2 = editPsw2.getText().toString();
        if (!Objects.equals(psw1, psw2)) {
            String message = "两次密码输入不一致！";
            showToast(message);
        } else {
            JSONObject params = new JSONObject();
            try {
                params.put("username", editUsername.getText().toString())
                        .put("email", editEmail.getText().toString())
                        .put("psw1", editPsw1.getText().toString())
                        .put("psw2", editPsw2.getText().toString())
                        .put("auth", "consumer");
            } catch (JSONException e) {
                e.printStackTrace();
            }
            new FetchApi(this, this).execute("register/", params.toString(), null);
            editReset();
        }
    }

    public void onClickReset(View view) {
        editReset();
    }

    private void editReset() {
        editUsername.setText("");
        editEmail.setText("");
        editPsw1.setText("");
        editPsw2.setText("");
    }

    private void showToast(String toastMessage) {
        Toast.makeText(this, toastMessage, Toast.LENGTH_SHORT).show();
    }

    @Override
    public void onTaskCompleted(String status, String type, String cookie, String content) {
        String message = "register: " + status;
        if (Objects.equals(status, "ok")) {
            message = "注册成功！请登录邮箱进行验证。";
            showToast(message);
            finish();
        } else {
            message = message + ", " + type;
            showToast(message);
        }
    }
}