package com.example.ssrmobile.ui.notifications;

import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;

import com.example.ssrmobile.BasicActivity;
import com.example.ssrmobile.DealStackAdapter;
import com.example.ssrmobile.R;
import com.loopeer.cardstack.CardStackView;

import static com.example.ssrmobile.BasicActivity.deals;

public class NotificationsFragment extends Fragment implements
        CardStackView.ItemExpendListener, BasicActivity.FragmentListener {
    private DealStackAdapter mStackAdapter;

    public View onCreateView(@NonNull LayoutInflater inflater,
                             ViewGroup container, Bundle savedInstanceState) {
        View root = inflater.inflate(R.layout.fragment_notifications, container, false);
        Log.d("xhs-map","Notification onCreateView");
        if (BasicActivity.isDealRendered){
            CardStackView mStackView=root.findViewById(R.id.stackview_deal);
            mStackView.setItemExpendListener(this);
            mStackAdapter=new DealStackAdapter(getContext());
            mStackView.setAdapter(mStackAdapter);

            mStackAdapter.updateData(deals);
        }
        return root;
    }

    @Override
    public void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        Log.d("xhs-map","Notification onCreate");
    }

    @Override
    public void onDestroy() {
        Log.d("xhs-map","Notification onDestroy");
        super.onDestroy();
    }

    @Override
    public void onItemExpend(boolean expend) {

    }

    @Override
    public void onTypeClick(String type, String message) {

    }
}