package com.example.ssrmobile;

import android.Manifest;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.BitmapFactory;
import android.os.Bundle;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.Button;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import androidx.fragment.app.Fragment;
import androidx.navigation.NavController;
import androidx.navigation.Navigation;
import androidx.navigation.ui.AppBarConfiguration;
import androidx.navigation.ui.NavigationUI;

import com.baidu.location.BDAbstractLocationListener;
import com.baidu.location.BDLocation;
import com.baidu.location.LocationClient;
import com.baidu.location.LocationClientOption;
import com.baidu.mapapi.map.BitmapDescriptor;
import com.baidu.mapapi.map.BitmapDescriptorFactory;
import com.baidu.mapapi.map.InfoWindow;
import com.baidu.mapapi.map.MyLocationData;
import com.baidu.mapapi.map.Overlay;
import com.baidu.mapapi.map.OverlayOptions;
import com.baidu.mapapi.map.TextOptions;
import com.baidu.mapapi.model.LatLng;
import com.example.ssrmobile.ui.dashboard.DashboardFragment;
import com.google.android.material.bottomnavigation.BottomNavigationView;
import com.loopeer.cardstack.CardStackView;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Objects;

import static com.example.ssrmobile.ui.dashboard.DashboardFragment.mBaiduMap;
import static com.example.ssrmobile.ui.dashboard.DashboardFragment.mUiSettings;


public class BasicActivity extends AppCompatActivity implements FetchApi.OnTaskCompleted, CardStackView.ItemExpendListener {

    private static final int SCAN_REQUEST_CODE = 200;
    private static final int PERMS_REQUEST_CODE = 202;
    public static double lat=121.501243;
    public static double lon=31.291311;
    public static String locationString=null;
    public static boolean isHomeRendered = false;
    public static boolean isDealRendered = false;
    public static ArrayList<Place> places;
    public static ArrayList<Deal> deals;

    private CardStackView mStackView;
    private HomeStackAdapter mStackAdapter;

    public LocationClient mLocationClient = null;
    private MyLocationListener myListener = new MyLocationListener();

    private FragmentListener fragmentListener;

    public interface FragmentListener{
        void onTypeClick(String type, String message);
    }

    public class MyLocationListener extends BDAbstractLocationListener {
        @Override
        public void onReceiveLocation(BDLocation location){
            //此处的BDLocation为定位结果信息类，通过它的各种get方法可获取定位相关的全部结果
            //以下只列举部分获取经纬度相关（常用）的结果信息
            //更多结果信息获取说明，请参照类参考中BDLocation类中的说明

            double latitude = location.getLatitude();    //获取纬度信息
            double longitude = location.getLongitude();    //获取经度信息
            float radius = location.getRadius();    //获取定位精度，默认值为0.0f

            String coorType = location.getCoorType();
            //获取经纬度坐标类型，以LocationClientOption中设置过的坐标类型为准

            int errorCode = location.getLocType();
            if (errorCode==61||errorCode==161){
                lon=longitude;
                lat=latitude;
                locationString=location.getCity()+location.getDistrict();
                Log.d("xhs-location",locationString);

                Fragment mMainNavFragment=getSupportFragmentManager().findFragmentById(R.id.nav_host_fragment);
                Fragment fragment=mMainNavFragment.getChildFragmentManager().getPrimaryNavigationFragment();
                fragmentListener=(FragmentListener)fragment;
                fragmentListener.onTypeClick("home",locationString);

                refreshPlaces();

                if (mBaiduMap!=null) {
                    MyLocationData locData=new MyLocationData.Builder()
                            .accuracy(radius)
                            .direction(location.getDirection())
                            .latitude(latitude)
                            .longitude(longitude).build();
                    mBaiduMap.setMyLocationData(locData);
                    mUiSettings.setCompassEnabled(true);
                }

            }
            //获取定位类型、定位错误返回码，具体信息可参照类参考中BDLocation类中的说明
            Log.d("xhs-test-latitude",String.valueOf(latitude));
            Log.d("xhs-test-longitude",String.valueOf(longitude));
            Log.d("xhs-test-radius",String.valueOf(radius));
            Log.d("xhs-test-coorType",coorType);
            Log.d("xhs-test-errorCode",String.valueOf(errorCode));
        }
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        Log.d("xhs-map","onCreate");
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_basic);
        BottomNavigationView navView = findViewById(R.id.nav_view);
        // Passing each menu ID as a set of Ids because each
        // menu should be considered as top level destinations.
        AppBarConfiguration appBarConfiguration = new AppBarConfiguration.Builder(
                R.id.navigation_home, R.id.navigation_dashboard, R.id.navigation_notifications)
                .build();
        NavController navController = Navigation.findNavController(this, R.id.nav_host_fragment);
        NavigationUI.setupActionBarWithNavController(this, navController, appBarConfiguration);
        NavigationUI.setupWithNavController(navView, navController);

        refreshPlaces();

        refreshDeals();

        String[] permissions = new String[]{
                Manifest.permission.WRITE_EXTERNAL_STORAGE,
                Manifest.permission.CAMERA,
                Manifest.permission.ACCESS_FINE_LOCATION,
                Manifest.permission.ACCESS_COARSE_LOCATION,
                Manifest.permission.ACCESS_WIFI_STATE,
                Manifest.permission.CHANGE_WIFI_STATE,
        };
        requestPermissions(permissions, PERMS_REQUEST_CODE);

        mLocationClient=new LocationClient(getApplicationContext());

        LocationClientOption option=new LocationClientOption();
        option.setLocationMode(LocationClientOption.LocationMode.Hight_Accuracy);
        option.setCoorType("bd09ll");
        option.setScanSpan(15*1000);
        option.setOpenGps(true);
        option.setWifiCacheTimeOut(5*60*1000);
        option.setIsNeedAddress(true);
        mLocationClient.setLocOption(option);

        mLocationClient.registerLocationListener(myListener);
        mLocationClient.start();
    }

    @Override
    protected void onDestroy() {
        mLocationClient.stop();
        super.onDestroy();
    }

    private void refreshDeals() {
        new FetchApi(this, this).execute("get/deal/", null, WelcomeActivity.sessionId);
    }

    private void refreshPlaces() {
        JSONObject param1 = new JSONObject();
        try {
            param1.put("longitude", lon)
                    .put("latitude", lat)
                    .put("nums", 10);
        } catch (JSONException e) {
            e.printStackTrace();
        }
        new FetchApi(this, this).execute("get/device/all/", param1.toString(), WelcomeActivity.sessionId);
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
//        return super.onCreateOptionsMenu(menu);
    }

    @Override
    public boolean onOptionsItemSelected(@NonNull MenuItem item) {
        switch (item.getItemId()) {
            case R.id.action_main_profile:
                Intent profileIntent=new Intent(this,ProfileActivity.class);
                startActivity(profileIntent);
                break;
            case R.id.action_main_changepsw:
                Intent changePswIntent=new Intent(this,ChangePswActivity.class);
                startActivity(changePswIntent);
                break;
            case R.id.action_main_qr_scan:
                Intent scanIntent = new Intent(this, ScanActivity.class);
                startActivityForResult(scanIntent, SCAN_REQUEST_CODE);
                break;
            case R.id.action_main_logout:
                new FetchApi(this, this).execute("logout/", null, WelcomeActivity.sessionId);
                break;
            case R.id.action_main_setting:
                break;
            default:
        }
        return true;
//        return super.onOptionsItemSelected(item);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent intent) {
        super.onActivityResult(requestCode, resultCode, intent);
        if (requestCode == SCAN_REQUEST_CODE && resultCode == RESULT_OK) {
            String input = intent.getStringExtra(ScanActivity.INTENT_EXTRA_RESULT);
            Log.d("xhs-test", "扫描结果:" + input);
            try {
                JSONObject jsonObject = new JSONObject(input);
                if (jsonObject.has("id")) {
                    Intent detailIntent = new Intent(this, DetailActivity.class);
                    detailIntent.putExtra("query", input);
                    startActivity(detailIntent);
                } else {
                    showToast("不支持该二维码。");
                }
            } catch (Exception e) {
                e.printStackTrace();
                showToast("不支持该二维码。");
            }
        }
    }

    private void showToast(String str) {
        Toast.makeText(this, str, Toast.LENGTH_SHORT).show();
    }

    @Override
    public void onTaskCompleted(String status, String type, String cookie, String content) {
        String message;
//        String message = "logout: " + status;
        if (Objects.equals(status, "ok")) {
            switch (type) {
                case "logout":
                    handleLogout();
                    break;
                case "get_device_all":
                    handleGetDevice(content);
                    break;
                case "get_deal":
                    handleGetDeal(content);
                    break;
                default:
            }
        } else {
            message = status + ", " + type;
            showToast(message);
        }
    }

    private void handleGetDeal(String s) {
        Log.d("xhs-test", "before handleGetDeal.");
        try {
            JSONObject jsonObject = new JSONObject(s);
            JSONArray content = jsonObject.getJSONArray("content");
            int contentLength = content.length();
            deals = new ArrayList<>(contentLength);
            for (int i = 0; i < contentLength; i++) {
                JSONObject jsonDeal = content.getJSONObject(i);
                int deviceId = jsonDeal.getInt("device_id");
                long timeStart = jsonDeal.getLong("start_time");
                long timeEnd = jsonDeal.getLong("end_time");
                String device = jsonDeal.getString("device");
                String place = jsonDeal.getString("location");
                Deal deal = new Deal(place, device, deviceId, timeStart, timeEnd);
                deals.add(deal);
            }
        } catch (JSONException e) {
            e.printStackTrace();
        }
        Log.d("xhs-test", "after handleGetDeal.");
        isDealRendered = true;
    }

    private void handleGetDevice(String contentString) {
        Log.d("xhs-test", "before handleGetDevice.");
        JSONObject jsonObject = null;
        try {
            jsonObject = new JSONObject(contentString);
            JSONArray content = jsonObject.getJSONArray("content");
            int contentLength = content.length();
//            boolean flag=mBaiduMap!=null;
            places = new ArrayList<>(contentLength);
            for (int i = 0; i < contentLength; i++) {
                JSONObject jsonPlace = content.getJSONObject(i);
                int place_id = jsonPlace.getInt("id");
                String place_name = jsonPlace.getString("name");
                double longitude = jsonPlace.getDouble("longitude");
                double latitude = jsonPlace.getDouble("latitude");

//                if (flag) {
//                    OverlayOptions mTextOptions=new TextOptions()
//                            .text(place_name)
//                            .bgColor(0xAAFFFF00)
//                            .fontSize(24)
//                            .fontColor(0xFFFF00FF)
//                            .rotate(0)
//                            .position(new LatLng(latitude,longitude));
//                    Overlay mText=mBaiduMap.addOverlay(mTextOptions);
//                }

                JSONArray jsonDevices = jsonPlace.getJSONArray("device");
                int deviceNum = jsonDevices.length();
                ArrayList<Device> devices = new ArrayList<>(deviceNum);
                for (int j = 0; j < deviceNum; j++) {
                    JSONObject jsonDevice = jsonDevices.getJSONObject(j);
                    int device_id = jsonDevice.getInt("id");
                    String device_name = jsonDevice.getString("name");
                    String status = jsonDevice.getString("status");
                    Device device = new Device(device_id, status, device_name);
                    devices.add(device);
                }
                Place place = new Place(longitude, latitude, place_name, place_id, devices);
                places.add(place);
            }
        } catch (JSONException e) {
            e.printStackTrace();
        }
        Log.d("xhs-test", "after handleGetDevice.");

        if (!isHomeRendered) {
            mStackView = findViewById(R.id.stackview_main);
            mStackView.setItemExpendListener(this);
            mStackAdapter = new HomeStackAdapter(this);
            mStackView.setAdapter(mStackAdapter);

            mStackAdapter.updateData(places);
            isHomeRendered = true;
        }else {
            if (mStackAdapter!=null) {
                mStackAdapter.updateData(places);
            }
        }
    }

    private void handleLogout() {
        String message;
        message = "登出成功！";
        showToast(message);
        WelcomeActivity.sessionId = null;
        isHomeRendered=false;
        isDealRendered=false;

        SharedPreferences.Editor preferencesEditor = WelcomeActivity.mPreferences.edit();
        preferencesEditor.clear();
        preferencesEditor.apply();

        Intent loginIntent = new Intent(this, MainActivity.class);
        startActivity(loginIntent);
        finish();
    }

    @Override
    public void onItemExpend(boolean expend) {

    }
}