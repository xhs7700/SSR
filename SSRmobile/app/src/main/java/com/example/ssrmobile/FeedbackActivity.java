package com.example.ssrmobile;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextUtils;
import android.text.TextWatcher;
import android.util.Log;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.Toast;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.Objects;

public class FeedbackActivity extends AppCompatActivity
        implements AdapterView.OnItemSelectedListener, FetchApi.OnTaskCompleted {
    private Spinner spinner;
    private EditText description;
    private Button buttonSubmit,buttonReset;
    private int deviceId;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_feedback);

        buttonSubmit = findViewById(R.id.button_feedback_submit);
        buttonReset = findViewById(R.id.button_feedback_reset);
        description = findViewById(R.id.feedback_description);
        spinner = findViewById(R.id.feedback_spinner);

        Intent intent = getIntent();
        deviceId = intent.getIntExtra("id", -1);

        description.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {

            }

            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
                buttonSubmit.setEnabled(!TextUtils.isEmpty(s));
            }

            @Override
            public void afterTextChanged(Editable s) {

            }
        });

        if (spinner != null) {
            spinner.setOnItemSelectedListener(this);
        }

        ArrayAdapter<CharSequence> adapter = ArrayAdapter.createFromResource(this,
                R.array.labels_array,
                android.R.layout.simple_spinner_item);
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);

        if (spinner != null) {
            spinner.setAdapter(adapter);
        }

    }

    @Override
    public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {

    }

    @Override
    public void onNothingSelected(AdapterView<?> parent) {

    }

    public void onClickSubmit(View view) {
        String descriptionStr=description.getText().toString();
        String type= (String) spinner.getSelectedItem();
        JSONObject params=new JSONObject();
        try {
            params.put("order_type",type)
                    .put("description",descriptionStr)
                    .put("id",deviceId);
        } catch (JSONException e) {
            e.printStackTrace();
        }
        new FetchApi(this,this).execute("add/order/",params.toString(),WelcomeActivity.sessionId);
    }

    public void onClickReset(View view) {
        description.setText("");
    }

    private void showToast(String toastMessage) {
        Toast.makeText(this,toastMessage,Toast.LENGTH_SHORT).show();
    }

    @Override
    public void onTaskCompleted(String status, String type, String cookie, String content) {
        String message="feedback: "+status;
        if (Objects.equals(status, "ok")){
            message="反馈提交成功！";
            showToast(message);
            finish();
        }else {
            message=message+", "+type;
            showToast(message);
        }
    }
}