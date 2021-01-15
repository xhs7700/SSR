package com.example.ssrmobile;

import androidx.appcompat.app.AppCompatActivity;

import android.os.Bundle;
import android.text.Editable;
import android.text.TextUtils;
import android.text.TextWatcher;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.Objects;

public class ChangePswActivity extends AppCompatActivity implements FetchApi.OnTaskCompleted {
    private EditText editOldPsw,editNewPsw;
    private Button buttonSubmit;
    boolean isOldPswEmpty=true,isNewPswEmpty=true;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_change_psw);

        editOldPsw=findViewById(R.id.editText_old_psw);
        editNewPsw=findViewById(R.id.editText_new_psw);
        buttonSubmit=findViewById(R.id.change_psw_button_submit);

        editOldPsw.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {

            }

            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
                isOldPswEmpty= TextUtils.isEmpty(s);
                buttonSubmit.setEnabled(!(isOldPswEmpty||isNewPswEmpty));
            }

            @Override
            public void afterTextChanged(Editable s) {

            }
        });
        editNewPsw.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {

            }

            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
                isNewPswEmpty=TextUtils.isEmpty(s);
                buttonSubmit.setEnabled(!(isOldPswEmpty||isNewPswEmpty));
            }

            @Override
            public void afterTextChanged(Editable s) {

            }
        });

    }

    public void onClickSubmit(View view) {
        String old_psw=editOldPsw.getText().toString();
        String new_psw=editNewPsw.getText().toString();
        if (Objects.equals(old_psw, new_psw)){
            showToast("两次密码输入一致！");
        }else {
            JSONObject params=new JSONObject();
            try {
                params.put("old_password",old_psw)
                        .put("new_password",new_psw);
            } catch (JSONException e) {
                e.printStackTrace();
            }
            new FetchApi(this,this).execute("set/psw/",params.toString(),WelcomeActivity.sessionId);
        }
    }

    public void onClickReset(View view) {
        editReset();
    }

    private void showToast(String toastMessage) {
        Toast.makeText(this,toastMessage,Toast.LENGTH_SHORT).show();
    }

    private void editReset() {
        editNewPsw.setText("");
        editOldPsw.setText("");
    }

    @Override
    public void onTaskCompleted(String status, String type, String cookie, String content) {
        String message="change_psw: "+status;
        if (Objects.equals(status, "ok")){
            message="修改密码成功！";
            showToast(message);
            finish();
        }else {
            message=message+", "+type;
            showToast(message);
        }
    }
}