package com.example.ssrmobile.ui.dashboard;

import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.lifecycle.Observer;
import androidx.lifecycle.ViewModelProvider;

import com.baidu.mapapi.map.BaiduMap;
import com.baidu.mapapi.map.MapStatus;
import com.baidu.mapapi.map.MapStatusUpdateFactory;
import com.baidu.mapapi.map.MapView;
import com.baidu.mapapi.map.Overlay;
import com.baidu.mapapi.map.OverlayOptions;
import com.baidu.mapapi.map.TextOptions;
import com.baidu.mapapi.map.UiSettings;
import com.baidu.mapapi.model.LatLng;
import com.example.ssrmobile.BasicActivity;
import com.example.ssrmobile.Place;
import com.example.ssrmobile.R;

import java.util.Objects;

public class DashboardFragment extends Fragment implements BasicActivity.FragmentListener {
    public static MapView mMapView = null;
    public static BaiduMap mBaiduMap;
    public static UiSettings mUiSettings;

    public View onCreateView(@NonNull LayoutInflater inflater,
                             ViewGroup container, Bundle savedInstanceState) {
        View root = inflater.inflate(R.layout.fragment_dashboard, container, false);

        mMapView=root.findViewById(R.id.bmapView);
        mMapView.showZoomControls(false);

        mBaiduMap=mMapView.getMap();
        mBaiduMap.setMyLocationEnabled(true);

        mUiSettings=mBaiduMap.getUiSettings();
        mUiSettings.setRotateGesturesEnabled(false);

        MapStatus.Builder builder=new MapStatus.Builder();
        builder.zoom(6.0f);
        mBaiduMap.setMapStatus(MapStatusUpdateFactory.newMapStatus(builder.build()));

        for (Place place:BasicActivity.places){
            OverlayOptions mTextOptions=new TextOptions()
                    .text(place.name)
                    .bgColor(0xAAFFFF00)
                    .fontSize(24)
                    .fontColor(0xFFFF00FF)
                    .rotate(0)
                    .position(new LatLng(place.latitude,place.longitude));
            Overlay mText=mBaiduMap.addOverlay(mTextOptions);
        }

        return root;
    }

//    @Override
//    public void onResume() {
//        Log.d("xhs-map","onResume");
//        super.onResume();
//        mMapView.onResume();
//    }
//
//    @Override
//    public void onPause() {
//        Log.d("xhs-map","onPause");
//        super.onPause();
////        mMapView.onPause();
//    }

//    @Override
//    public void onDestroy() {
//        Log.d("xhs-map","onDestroy");
//        mBaiduMap.clear();
//        mMapView.onDestroy();
//        super.onDestroy();
//    }

    private void showToast(String str) {
        Toast.makeText(getContext(), str, Toast.LENGTH_LONG).show();
    }

    @Override
    public void onTypeClick(String type, String message) {
        if (Objects.equals(type, "dashboard")){

        }
    }
}