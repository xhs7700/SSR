package com.example.ssrmobile;

import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.View;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
import java.util.Objects;

public class ProfileActivity extends AppCompatActivity implements FetchApi.OnTaskCompleted {
    private TextView textUsername, textEmail, textCreatedTime, textAsset;
    private TextView textNum15, textNum30, textNum60, textNum120;
    private TextView textTotal;
    private int costTotal = 0, asset = 0, timeTotal = 0;
    private ImageButton buttonMinus15, buttonPlus15, buttonMinus30, buttonPlus30;
    private ImageButton buttonMinus60, buttonPlus60, buttonMinus120, buttonPlus120;
    private Button buttonSubmit;

    public void onClickSubmit(View view) {
        JSONObject params = new JSONObject();
        try {
            params.put("asset", asset + timeTotal);
        } catch (JSONException e) {
            e.printStackTrace();
        }
        new FetchApi(this, this).execute("set/asset/", params.toString(), WelcomeActivity.sessionId);
    }

    public void onClickReset(View view) {
        editReset();
    }

    private void editReset() {
        textNum15.setText("0");
        textNum30.setText("0");
        textNum60.setText("0");
        textNum120.setText("0");
        String textTotalStr = getString(R.string.text_profile_total) + "0";
        textTotal.setText(textTotalStr);
        costTotal = 0;
        timeTotal = 0;
        buttonSubmit.setEnabled(false);
    }
//    private int counter15=0,counter30=0,counter60=0,counter120=0;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_profile);
        {
            textUsername = findViewById(R.id.text_profile_username);
            textEmail = findViewById(R.id.text_profile_email);
            textCreatedTime = findViewById(R.id.text_profile_time);
            textAsset = findViewById(R.id.text_profile_asset);
            textNum15 = findViewById(R.id.textnum15);
            textNum30 = findViewById(R.id.textnum30);
            textNum60 = findViewById(R.id.textnum60);
            textNum120 = findViewById(R.id.textnum120);
            buttonMinus15 = findViewById(R.id.button_minus15);
            buttonMinus30 = findViewById(R.id.button_minus30);
            buttonMinus60 = findViewById(R.id.button_minus60);
            buttonMinus120 = findViewById(R.id.button_minus120);
            buttonPlus15 = findViewById(R.id.button_plus15);
            buttonPlus30 = findViewById(R.id.button_plus30);
            buttonPlus60 = findViewById(R.id.button_plus60);
            buttonPlus120 = findViewById(R.id.button_plus120);
            textTotal = findViewById(R.id.text_profile_total);
        }

        buttonMinus15.setEnabled(false);
        buttonMinus30.setEnabled(false);
        buttonMinus60.setEnabled(false);
        buttonMinus120.setEnabled(false);

        textNum15.addTextChangedListener(new ProfileTextWatcher(buttonMinus15));
        textNum30.addTextChangedListener(new ProfileTextWatcher(buttonMinus30));
        textNum60.addTextChangedListener(new ProfileTextWatcher(buttonMinus60));
        textNum120.addTextChangedListener(new ProfileTextWatcher(buttonMinus120));

        {
            buttonMinus15.setOnClickListener(new ProfileOnClickListener(textNum15, false, 30, 15));
            buttonMinus30.setOnClickListener(new ProfileOnClickListener(textNum30, false, 45, 30));
            buttonMinus60.setOnClickListener(new ProfileOnClickListener(textNum60, false, 60, 60));
            buttonMinus120.setOnClickListener(new ProfileOnClickListener(textNum120, false, 90, 120));
            buttonPlus15.setOnClickListener(new ProfileOnClickListener(textNum15, true, 30, 15));
            buttonPlus30.setOnClickListener(new ProfileOnClickListener(textNum30, true, 45, 30));
            buttonPlus60.setOnClickListener(new ProfileOnClickListener(textNum60, true, 60, 60));
            buttonPlus120.setOnClickListener(new ProfileOnClickListener(textNum120, true, 90, 120));
        }

        buttonSubmit = findViewById(R.id.button_profile_submit);

        String textTotalStr = getString(R.string.text_profile_total) + "0";
        textTotal.setText(textTotalStr);

        new FetchApi(this, this).execute("get/profile/", null, WelcomeActivity.sessionId);
    }

    private void showToast(String toastMessage) {
        Toast.makeText(this, toastMessage, Toast.LENGTH_SHORT).show();
    }

    @Override
    public void onTaskCompleted(String status, String type, String cookie, String s) {
        if (Objects.equals(status, "ok")) {
            switch (type) {
                case "get_user_profile":
                    handleGetProfile(s);
                    break;
                default:
                    new FetchApi(this, this).execute("get/profile/", null, WelcomeActivity.sessionId);
            }
        } else {
            String message = "get_profile: " + status + ", " + type;
            showToast(message);
        }
    }

    private void handleGetProfile(String s) {
        try {
            JSONObject jsonObject = new JSONObject(s);
            JSONArray content = jsonObject.getJSONArray("content");
            JSONObject jsonProfile = content.getJSONObject(0);

            String username = jsonProfile.getString("name");
            String email = jsonProfile.getString("email");
            long createdTime = jsonProfile.getLong("created_time");
            asset = jsonProfile.getInt("asset");
            int hour = asset / 60, minute = asset % 60;

            SimpleDateFormat ft = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.CHINA);
            String textCreatedTimeStr = getString(R.string.text_profile_created_time) + ft.format(new Date(createdTime));
            String textUsernameStr = getString(R.string.text_profile_username) + username;
            String textEmailStr = getString(R.string.text_profile_email) + email;
            String textAssetStr = getString(R.string.text_profile_asset) + hour + "小时" + minute + "分钟";

            textUsername.setText(textUsernameStr);
            textEmail.setText(textEmailStr);
            textCreatedTime.setText(textCreatedTimeStr);
            textAsset.setText(textAssetStr);
            editReset();
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    class ProfileTextWatcher implements TextWatcher {
        private final ImageButton releventButton;

        ProfileTextWatcher(ImageButton button) {
            releventButton = button;
        }

        @Override
        public void beforeTextChanged(CharSequence s, int start, int count, int after) {

        }

        @Override
        public void onTextChanged(CharSequence s, int start, int before, int count) {
            int num = Integer.parseInt(s.toString());
            releventButton.setEnabled(num != 0);
        }

        @Override
        public void afterTextChanged(Editable s) {

        }
    }

    class ProfileOnClickListener implements View.OnClickListener {
        private final TextView textView;
        private final boolean isPlus;
        private final int cost, time;

        ProfileOnClickListener(TextView textView, boolean isPlus, int cost, int time) {
            this.textView = textView;
            this.isPlus = isPlus;
            this.cost = cost;
            this.time = time;
        }

        @Override
        public void onClick(View v) {
            int counter = Integer.parseInt(textView.getText().toString());
            if (isPlus) {
                counter++;
                costTotal += cost;
                timeTotal += time;
            } else {
                counter--;
                costTotal -= cost;
                timeTotal -= time;
            }

            buttonSubmit.setEnabled(costTotal != 0);

            String text = String.valueOf(counter);
            String textTotalStr = getString(R.string.text_profile_total) + costTotal;
            textView.setText(text);
            textTotal.setText(textTotalStr);
        }
    }
}