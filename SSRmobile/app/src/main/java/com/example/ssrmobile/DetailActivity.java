package com.example.ssrmobile;

import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.CompoundButton;
import android.widget.TextView;
import android.widget.Toast;
import android.widget.ToggleButton;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.Objects;

public class DetailActivity extends AppCompatActivity implements FetchApi.OnTaskCompleted {
    private final Handler handler = new Handler();
    private TextView textPlace, textDevice, textDeviceID, textStatus, textAsset;
    private ToggleButton buttonTimer;
    private long timeStart, timeEnd;
    private int asset, currentAsset, deviceId;
    private String placeStr,deviceStr;

    private final Runnable runnable = new Runnable() {
        @Override
        public void run() {
            getCurrentAsset();
            setTextAsset(currentAsset);
            handler.postDelayed(this, 1000);
        }
    };

    private void getCurrentAsset() {
        long second = System.currentTimeMillis() / 1000;
        int interval = (int) (second - timeStart / 1000);
        currentAsset = asset - interval;
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_detail);

        {
            textAsset = findViewById(R.id.text_detail_asset);
            textDevice = findViewById(R.id.text_detail_device);
            textDeviceID = findViewById(R.id.text_detail_device_id);
            textPlace = findViewById(R.id.text_detail_place);
            textStatus = findViewById(R.id.text_detail_status);
            buttonTimer = findViewById(R.id.button_detail_timer);
        }

        Intent intent = getIntent();
        String query = intent.getStringExtra("query");
        new FetchApi(this, this).execute("get/device/single/", query, WelcomeActivity.sessionId);
        new FetchApi(this, this).execute("get/asset/", null, WelcomeActivity.sessionId);
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.menu_detail, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(@NonNull MenuItem item) {
        switch (item.getItemId()) {
            case R.id.action_detail_feedback:
                Intent feedbackIntent=new Intent(this,FeedbackActivity.class);
                feedbackIntent.putExtra("id",deviceId);
                startActivity(feedbackIntent);
                break;
            default:
        }
        return true;
    }

    @Override
    public void onTaskCompleted(String status, String type, String cookie, String content) {
        String message;
        if (Objects.equals(status, "ok")) {
            switch (type) {
                case "get_device_single":
                    handleGetDeviceSingle(content);
                    break;
                case "get_asset":
                    handleGetAsset(content);
                    break;
                default:
            }
        }
    }

    private void handleGetAsset(String s) {
        try {
            JSONObject jsonObject = new JSONObject(s);
            JSONArray content = jsonObject.getJSONArray("content");
            JSONObject object = content.getJSONObject(0);

            int asset = object.getInt("asset");
            this.asset = asset;
            this.currentAsset = asset;
            if (asset == 0) {
                buttonTimer.setEnabled(false);
            }

            setTextAsset(asset);
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    private void setTextAsset(int asset) {
        int minute = asset / 60;
        int second = asset % 60;
        String minuteString = String.valueOf(minute);
        String secondString = String.valueOf(second);
        if (minute < 10) {
            minuteString = "0" + minuteString;
        }
        if (second < 10) {
            secondString = "0" + secondString;
        }
        String assetString = minuteString + ":" + secondString;
        textAsset.setText(assetString);
    }

    private void handleGetDeviceSingle(String s) {
        try {
            JSONObject jsonObject = new JSONObject(s);
            JSONArray content = jsonObject.getJSONArray("content");
            JSONObject device = content.getJSONObject(0);

            deviceId = device.getInt("id");
            deviceStr=device.getString("name");
            placeStr=device.getString("location");
            String id = getString(R.string.title_detail_device_id) + deviceId;
            String name = getString(R.string.title_detail_device) + deviceStr;
            String status = device.getString("status");
            String statusString = getString(R.string.title_detail_status) + status;
            String place = getString(R.string.title_detail_place) + placeStr;

            if (!Objects.equals(status, "在线")) {
                buttonTimer.setEnabled(false);
            } else {
                buttonTimer.setOnCheckedChangeListener(new OnCheckedChangeListener(this));
            }

            textPlace.setText(place);
            textDevice.setText(name);
            textDeviceID.setText(id);
            textStatus.setText(statusString);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private void showToast(String str) {
        Toast.makeText(this, str, Toast.LENGTH_SHORT).show();
    }

    @Override
    protected void onPause() {
        if (handler.hasCallbacks(runnable)) {
            timeEnd = System.currentTimeMillis();
            getCurrentAsset();
            setTextAsset(currentAsset);
            asset = currentAsset;
            handler.removeCallbacks(runnable);

            JSONObject param1 = new JSONObject();
            try {
                param1.put("asset", asset);
            } catch (JSONException e) {
                e.printStackTrace();
            }
            new FetchApi(this, this).execute("set/asset/",
                    param1.toString(),
                    WelcomeActivity.sessionId);

            JSONObject param2 = new JSONObject();
            try {
                param2.put("id", deviceId)
                        .put("start_time", timeStart)
                        .put("end_time", timeEnd);
            } catch (JSONException e) {
                e.printStackTrace();
            }
            new FetchApi(this, this).execute("add/deal/",
                    param2.toString(),
                    WelcomeActivity.sessionId);
            BasicActivity.deals.add(new Deal(placeStr,deviceStr,deviceId,timeStart,timeEnd));
        }
        super.onPause();
    }

    class OnCheckedChangeListener implements CompoundButton.OnCheckedChangeListener {
        Context context;

        OnCheckedChangeListener(Context context) {
            this.context = context;
        }

        @Override
        public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
            if (isChecked) {
                timeStart = System.currentTimeMillis();
                handler.postDelayed(runnable, 1000);
            } else {
                timeEnd = System.currentTimeMillis();
                getCurrentAsset();
                setTextAsset(currentAsset);
                asset = currentAsset;
                handler.removeCallbacks(runnable);

                JSONObject param1 = new JSONObject();
                try {
                    param1.put("asset", asset);
                } catch (JSONException e) {
                    e.printStackTrace();
                }
                new FetchApi(context, (FetchApi.OnTaskCompleted) context).execute("set/asset/",
                        param1.toString(),
                        WelcomeActivity.sessionId);

                JSONObject param2 = new JSONObject();
                try {
                    param2.put("id", deviceId)
                            .put("start_time", timeStart)
                            .put("end_time", timeEnd);
                } catch (JSONException e) {
                    e.printStackTrace();
                }
                new FetchApi(context, (FetchApi.OnTaskCompleted) context).execute("add/deal/",
                        param2.toString(),
                        WelcomeActivity.sessionId);
                BasicActivity.deals.add(new Deal(placeStr,deviceStr,deviceId,timeStart,timeEnd));
            }
        }
    }

}