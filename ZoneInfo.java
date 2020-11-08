import java.io.FileWriter;
import java.util.TimeZone;

public class ZoneInfo {
    public static final int MS_PER_H = 1000 * 3600;
    public static final int MS_PER_M = 1000 * 60;

    public static String processOffset(int offset) {
        String[] idArr = TimeZone.getAvailableIDs(offset);
        String buffer = "";
        int hour = (Math.abs(offset) / MS_PER_H);
        int min = (Math.abs(offset) % MS_PER_H)/MS_PER_M;

        if((null != idArr) && (0 < idArr.length)){
            if(0 > offset) {
                buffer += String.format("\"-%02d:%02d\": [", hour, min);
            } else if (0 == offset) {
                buffer += "\"00:00\": [";
            } else {
                buffer += String.format("\"+%02d:%02d\": [", hour, min);
            }

            for(int i = 0; i < idArr.length; i++) {
                String zoneId = idArr[i];

                buffer += String.format("\"%s\", ", zoneId);
            }

            buffer = buffer.substring(0, buffer.length() - ", ".length());

            buffer += "]\n";
        }

        return buffer;
    }

    public static void main(String[] args) {
        int MIN_OFFSET = -15 * MS_PER_H;
        int MAX_OFFSET = 15 * MS_PER_H;
        int offset = MIN_OFFSET;
        boolean isFirst = true;

        try {
            FileWriter fw = new FileWriter("zoneinfo.json");

            fw.write("{\n");
            for (; offset < MAX_OFFSET; offset += MS_PER_H/4) {
                String buffer = processOffset(offset);
                if("" != buffer) {
                    if(isFirst) {
                        isFirst = false;
                    } else {
                        fw.write(",");
                    }

                    fw.write(buffer);
                }
            }

            fw.write("}");

            fw.close();
        } catch (Exception e) {
            System.out.println(e);
        }

        return;
    }
}