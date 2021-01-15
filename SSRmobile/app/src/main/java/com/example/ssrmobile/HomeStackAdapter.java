package com.example.ssrmobile;

import android.content.Context;
import android.graphics.BlendMode;
import android.graphics.BlendModeColorFilter;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import com.loopeer.cardstack.CardStackView;
import com.loopeer.cardstack.StackAdapter;

import java.util.ArrayList;

import static androidx.core.content.ContextCompat.getColor;

public class HomeStackAdapter extends StackAdapter<Place> {
    private static final Integer[] COLORS = new Integer[]{
            R.color.color_1,
            R.color.color_2,
            R.color.color_3,
            R.color.color_4,
            R.color.color_5,
            R.color.color_6,
            R.color.color_7,
            R.color.color_8,
            R.color.color_9,
            R.color.color_10,
            R.color.color_11,
            R.color.color_12,
            R.color.color_13,
            R.color.color_14,
            R.color.color_15,
            R.color.color_16,
            R.color.color_17,
            R.color.color_18,
            R.color.color_19,
            R.color.color_20,
            R.color.color_21,
            R.color.color_22,
            R.color.color_23,
            R.color.color_24,
            R.color.color_25,
            R.color.color_26
    };

    public HomeStackAdapter(Context context) {
        super(context);
    }

    @Override
    public void bindView(Place data, int position, CardStackView.ViewHolder holder) {
        ColorItemViewHolder h = (ColorItemViewHolder) holder;
        h.onBind(data, position);
    }

    @Override
    protected CardStackView.ViewHolder onCreateView(ViewGroup parent, int viewType) {
        View view;
        view = getLayoutInflater().inflate(R.layout.list_card_item, parent, false);
        return new ColorItemViewHolder(view);
    }

    static class ColorItemViewHolder extends CardStackView.ViewHolder {
        View mLayout;
        View mContainerContent;
        TextView mTextTitle;
        TextView mTextContent;

        public ColorItemViewHolder(View view) {
            super(view);
            mLayout = view.findViewById(R.id.frame_list_card_item);
            mContainerContent = view.findViewById(R.id.container_list_content);
            mTextTitle = view.findViewById(R.id.text_list_card_title);
            mTextContent = view.findViewById(R.id.text_list_card_content);
        }

        @Override
        public void onItemExpand(boolean b) {
            mContainerContent.setVisibility(b ? View.VISIBLE : View.GONE);
        }

        public void onBind(Place place, int position) {
            int colorsLength = COLORS.length;
            BlendModeColorFilter colorFilter = new BlendModeColorFilter(getColor(getContext(),
                    COLORS[position % colorsLength]), BlendMode.SRC_IN);
            mLayout.getBackground().setColorFilter(colorFilter);
            String text = (position + 1) + " -- " + place.name;
            mTextTitle.setText(text);
            ArrayList<String> content = new ArrayList<>();
            for (Device device : place.devices) {
                content.add("名字：" + device.name + ";状态：" + device.status);
            }
            String ans = "该地点暂无设备";
            if (content.size() != 0) {
                ans = String.join("\n", content);
            }
            mTextContent.setText(ans);
        }

    }

}
