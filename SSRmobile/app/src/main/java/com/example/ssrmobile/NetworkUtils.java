package com.example.ssrmobile;

import android.util.Log;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Map;

public class NetworkUtils {
//    private static final String BASE_URL = "http://45.77.18.246:8000/users/";
//    private static final String BASE_URL = "http://192.168.1.105:8000/users/";
    private static final String LOG_TAG = "xhs-network-test";

    static String[] fetch(String urlPart, String query, String cookie) {
        String url = BuildConfig.BASE_URL + urlPart;
        URL builtUrl = null;
        try {
            builtUrl = new URL(url);
        } catch (MalformedURLException e) {
            e.printStackTrace();
        }
        HttpURLConnection conn = null;
        BufferedReader reader = null;
        String JSONString = null;
        try {
            conn = (HttpURLConnection) builtUrl.openConnection();
            conn.setDoInput(true);
            conn.setDoOutput(true);
            conn.setRequestMethod("POST");
            conn.setUseCaches(false);
            conn.setInstanceFollowRedirects(true);
            conn.setRequestProperty("Content-Type", "application/json");
            if (cookie != null) {
                conn.setRequestProperty("Cookie", cookie);
            }
            conn.connect();
            if (query != null) {
                OutputStream os = conn.getOutputStream();
                os.write(query.getBytes(StandardCharsets.UTF_8));
            }

            reader = new BufferedReader(
                    new InputStreamReader(conn.getInputStream()));
            String line;
            StringBuilder builder = new StringBuilder();
            while ((line = reader.readLine()) != null) {
                builder.append(line);
                builder.append("\n");
            }
            JSONString = builder.toString();
            Log.d(LOG_TAG, JSONString);
            Map<String, List<String>> cookies = conn.getHeaderFields();
            List<String> setCookies = cookies.get("Set-Cookie");
            String setCookie = null;
            if (setCookies != null) {
                setCookie = setCookies.get(0);
            }
            return new String[]{JSONString, setCookie, urlPart};
        } catch (IOException e) {
            e.printStackTrace();
            return new String[]{"{}", null, urlPart};
        } finally {
            if (conn != null) {
                conn.disconnect();
            }
            if (reader != null) {
                try {
                    reader.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }
    }
}
