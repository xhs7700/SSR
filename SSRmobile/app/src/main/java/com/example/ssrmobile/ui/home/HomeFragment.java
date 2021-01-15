package com.example.ssrmobile.ui.home;

import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.fragment.app.Fragment;

import com.example.ssrmobile.BasicActivity;
import com.example.ssrmobile.HomeStackAdapter;
import com.example.ssrmobile.R;
import com.loopeer.cardstack.CardStackView;

import java.util.Objects;

import static com.example.ssrmobile.BasicActivity.places;

public class HomeFragment extends Fragment implements
        CardStackView.ItemExpendListener, BasicActivity.FragmentListener {
    HomeStackAdapter mStackAdapter;
    private TextView textLocation;

    public View onCreateView(@NonNull LayoutInflater inflater,
                             ViewGroup container, Bundle savedInstanceState) {
        View root = inflater.inflate(R.layout.fragment_home, container, false);
        textLocation=root.findViewById(R.id.text_home_location);
        textLocation.setText("地区："+BasicActivity.locationString);
        if (BasicActivity.isHomeRendered) {
            Log.d("xhs-test", "onCreateView");
            CardStackView mStackView = root.findViewById(R.id.stackview_main);
            mStackView.setItemExpendListener(this);
            mStackAdapter = new HomeStackAdapter(getContext());
            mStackView.setAdapter(mStackAdapter);

            mStackAdapter.updateData(places);
        }

        return root;
    }

    @Override
    public void onItemExpend(boolean expend) {

    }

    @Override
    public void onTypeClick(String type, String message) {
        if (Objects.equals(type, "home")){
            String textLocationStr="地区："+message;
            textLocation.setText(textLocationStr);
        }
    }
}