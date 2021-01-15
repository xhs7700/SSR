package com.example.ssrmobile;

import android.content.Context;
import android.os.AsyncTask;
import android.util.Log;

import org.json.JSONArray;
import org.json.JSONObject;

import java.lang.ref.WeakReference;

public class FetchApi extends AsyncTask<String, Void, String[]> {
    private static final String LOG_TAG = "xhs-test";
    private final WeakReference<Context> context;
    private final OnTaskCompleted mListener;
//    private Context context;

    FetchApi(Context context, OnTaskCompleted listener) {
        this.context = new WeakReference<>(context);
        mListener = listener;
//        this.context=context;
    }

    @Override
    protected String[] doInBackground(String... strings) {
        String urlPart = strings[0];
        String query = strings[1];
        String cookie = strings[2];
        return NetworkUtils.fetch(urlPart, query, cookie);
    }

    @Override
    protected void onPostExecute(String[] strings) {
        String JSONString = strings[0];
        String cookie = strings[1];
        String urlPart = strings[2];

        String status = null;
        String type = null;
        String JSONContentString = null;

        try {
            JSONObject resp = new JSONObject(JSONString);
            status = resp.getString("status");
            type = resp.getString("type");
            JSONArray items = null;
            if (resp.has("content")) {
                items = resp.getJSONArray("content");
            }
            if (items != null) {
                JSONObject obj = new JSONObject();
                obj.put("content", items);
                JSONContentString = obj.toString();
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        mListener.onTaskCompleted(status, type, cookie, JSONContentString);
        Log.d(LOG_TAG, WelcomeActivity.sessionId == null ? "null" : WelcomeActivity.sessionId);
    }

    interface OnTaskCompleted {
        void onTaskCompleted(String status, String type, String cookie, String content);
    }
}
