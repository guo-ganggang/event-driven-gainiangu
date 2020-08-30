package test;
 
import java.io.BufferedReader;
import java.io.File;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.PrintStream;
import java.util.List;

import com.gargoylesoftware.htmlunit.WebClient;
import com.gargoylesoftware.htmlunit.html.HtmlAnchor;
import com.gargoylesoftware.htmlunit.html.HtmlDivision;
import com.gargoylesoftware.htmlunit.html.HtmlPage;
import com.gargoylesoftware.htmlunit.html.HtmlTableHeaderCell;

public class xlcj {
	public static void main(String args[]) throws Exception {
		xlcj test1 = new xlcj();
		test1.readUrl();
		//test1.homePage("http://vip.stock.finance.sina.com.cn/mkt/#gn_qszc", "券商重仓");
	}
	
	public void readUrl() throws Exception {
		File input = new File("J:/crawl/xinlangcaijing_first_letters.csv");
		@SuppressWarnings("resource")
		BufferedReader br = new BufferedReader(new FileReader(input));
		String line = br.readLine();
		while(line != null) {
			String abbr = line.split("\t")[1];
			String chinese = line.split("\t")[0];
			String url = "http://vip.stock.finance.sina.com.cn/mkt/#gn_"+abbr;
			homePage(url, chinese);
			line = br.readLine();
		}
	}
	
	public void homePage(String url, String chinese) throws Exception {
	    try (final WebClient webClient = new WebClient()) {
	        //String url = "http://stock.jrj.com.cn/concept/conceptdetail/conceptDetail_360syh.shtml";
	        // 1 启动JS  
	        webClient.getOptions().setJavaScriptEnabled(true);  
	        // 2 禁用Css，可避免自动二次请求CSS进行渲染  
	        webClient.getOptions().setCssEnabled(false);  
	        // 3 启动客户端重定向  
	        webClient.getOptions().setRedirectEnabled(true);  
	      
	        // 4 js运行错误时，是否抛出异常  
	        webClient.getOptions().setThrowExceptionOnScriptError(false);  
	        // 5 设置超时  
	        webClient.getOptions().setTimeout(50000);  
	          
	        final HtmlPage page = webClient.getPage(url);  
	        // 等待JS驱动dom完成获得还原后的网页  
	        webClient.waitForBackgroundJavaScript(60000);  
	        
	        FileOutputStream out=new FileOutputStream("J:\\crawl\\output\\sina\\"+chinese+".csv");
            PrintStream p = new PrintStream(out);
            
            HtmlPage newpage = page;
            
            HtmlDivision div;
            
            div = (HtmlDivision)newpage.getElementById("tbl_wrap");
	        System.out.println(div.asText());
	        List<Object> thList = div.getByXPath("table/tbody/tr/th");
	        for(int i=0; i<thList.size(); i++) {
	        	//String text = ((HtmlTableHeaderCell) thList.get(i)).asText();
	        	if((i+1)%4==1) {
	        		p.print(((HtmlTableHeaderCell) thList.get(i)).asText()+",");
	        	}
	        	else if((i+1)%4==2)
	        		p.println(((HtmlTableHeaderCell) thList.get(i)).asText());
	        }
	        
	        HtmlDivision button = (HtmlDivision)page.getElementById("list_page_btn_2");
	        
	        HtmlAnchor anchor = null; 
	        if(button.getByXPath("a").size() > 0) {
	        	anchor = (HtmlAnchor)button.getByXPath("a").get(0);
	        	System.out.println(anchor.asXml());
	        }
            
            while(anchor != null) {
            	newpage = anchor.click();
		        webClient.waitForBackgroundJavaScript(10000);  
		        button = (HtmlDivision)newpage.getElementById("list_page_btn_2");
		        if(button.getByXPath("a").size() > 0) {
		        	anchor = (HtmlAnchor)button.getByXPath("a").get(0);
		        	System.out.println(anchor.asXml());
		        }
		        else
		        	anchor = null;
    	        div = (HtmlDivision)newpage.getElementById("tbl_wrap");
    	        System.out.println(div.asText());
    	        thList = div.getByXPath("table/tbody/tr/th");
		        for(int i=0; i<thList.size(); i++) {
		        	//String text = ((HtmlTableHeaderCell) thList.get(i)).asText();
		        	if((i+1)%4==1) {
		        		p.print(((HtmlTableHeaderCell) thList.get(i)).asText()+",");
		        	}
		        	else if((i+1)%4==2)
		        		p.println(((HtmlTableHeaderCell) thList.get(i)).asText());
		        }
		        
            }
	        p.close();
	        webClient.close();
	        //System.out.println(div.asText());

	    }
	}
}