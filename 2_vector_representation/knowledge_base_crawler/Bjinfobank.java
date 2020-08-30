package test;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.PrintStream;
import java.net.URLEncoder;
import java.util.List;

import com.gargoylesoftware.htmlunit.WebClient;
import com.gargoylesoftware.htmlunit.html.HtmlAnchor;
import com.gargoylesoftware.htmlunit.html.HtmlDivision;
import com.gargoylesoftware.htmlunit.html.HtmlPage;
import com.gargoylesoftware.htmlunit.html.HtmlSpan;
import com.gargoylesoftware.htmlunit.html.HtmlTableDataCell;
import com.gargoylesoftware.htmlunit.html.HtmlTableRow;

public class Bjinfobank {
	public static void main(String args[]) throws Exception {
		Bjinfobank test1 = new Bjinfobank();
		test1.readUrl();
	}
	
	public void readUrl() throws Exception {
		File input = new File("J:/crawl/stock_name.csv");
		@SuppressWarnings("resource")
		BufferedReader br = new BufferedReader(new FileReader(input));
		String line = br.readLine();
		int i=1;
		while(line != null) {
			if(i>=397)
				homePage(line);
			System.out.println(line);
			line = br.readLine();
			i++;
		}
	}
	
	public void homePage(String line) throws Exception {
		String encode = URLEncoder.encode(line, "utf-8");
	    try (final WebClient webClient = new WebClient()) {
	        String url = "http://www.bjinfobank.com/DataList.do?page=1&db=HK&rl=2&iw="+encode+"&query=all&pageSize=100&endTime=&metiaName=&typeName=&starTime=&metiaLevel=&method=DataList&className=&areaForArt=&myorder=SUTM&areaForArt=";
	        
	        // 1 启动JS  
	        webClient.getOptions().setJavaScriptEnabled(false);  
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
	        //webClient.waitForBackgroundJavaScript(1);  
	        
	        HtmlDivision div = (HtmlDivision)page.getElementById("left");
	        
	        List<Object> trList = div.getByXPath("table/tbody/tr");
	        
	        FileOutputStream out=new FileOutputStream("J:\\crawl\\output\\bjinfobank\\"+line+".csv");
            PrintStream p = new PrintStream(out); 
	        
	        for(int i=1; i<trList.size()-1; i++) {
	        	if (i%2==1) {
	        		List<Object> aList = ((HtmlTableRow) trList.get(i)).getByXPath("td/a");
	        		HtmlAnchor a = (HtmlAnchor) aList.get(0);
	        		String output = a.asXml().split("title=\"")[1].split("\">")[0];
	        		p.print(output+",");
	        		List<Object> tdList = ((HtmlTableRow) trList.get(i)).getByXPath("td");
	        		if(tdList.size()>2) {
	        			HtmlTableDataCell td = (HtmlTableDataCell) tdList.get(2);
		        		p.print(td.asText()+",");
	        		}	        		
	        	}
	        	else {
	        		List<Object> tdList2 = ((HtmlTableRow) trList.get(i)).getByXPath("td");
	        		for(int k = 1; k < tdList2.size()-2; k++) {
	        			p.print(((HtmlTableDataCell) tdList2.get(k)).asText()+",");
	        		}
	        		p.println(((HtmlTableDataCell) tdList2.get(tdList2.size()-2)).asText());
	        	}
	        }
	        	
	        HtmlDivision divbankbody = (HtmlDivision)page.getElementById("bankbody");
	        
	        List<Object> spanList = divbankbody.getByXPath("div/form/div/div/div/table/tbody/tr/td/span");
	        
	        HtmlSpan span = (HtmlSpan) spanList.get(0);
	        
	        Integer spanNum = Integer.parseInt(span.asText().replace(",",""));
	        	
	        int pageNum = spanNum / 100 + 1; 
	        //System.out.println(pageNum);
	        
	        if (pageNum < 2) {
	        	p.close();
	        	return;
	        }
	        
	        if(pageNum > 100)
	        	pageNum = 100;
	        	
	        for(int j = 2; j <= pageNum; j++) {
	        	String url2 = "http://www.bjinfobank.com/DataList.do?page="+j+"&db=HK&rl=2&iw="+encode+"&query=all&pageSize=100&endTime=&metiaName=&typeName=&starTime=&metiaLevel=&method=DataList&className=&areaForArt=&myorder=SUTM&areaForArt=";
	        	final HtmlPage page2 = webClient.getPage(url2);  
		        // 等待JS驱动dom完成获得还原后的网页  
		        //webClient.waitForBackgroundJavaScript(1);  
		        
		        HtmlDivision div2 = (HtmlDivision)page2.getElementById("left");
		        
		        List<Object> trList2 = div2.getByXPath("table/tbody/tr");
		        
		        for(int i=1; i<trList2.size()-1; i++) {
		        	if (i%2==1) {
		        		List<Object> aList2 = ((HtmlTableRow) trList2.get(i)).getByXPath("td/a");
		        		HtmlAnchor a2 = (HtmlAnchor) aList2.get(0);
		        		String output = a2.asXml().split("title=\"")[1].split("\">")[0];
		        		p.print(output+",");
		        		List<Object> tdList2 = ((HtmlTableRow) trList2.get(i)).getByXPath("td");
		        		if(tdList2.size()>2) {
		        			HtmlTableDataCell td2 = (HtmlTableDataCell) tdList2.get(2);
		        			p.print(td2.asText()+",");
		        		}
		        	}
		        	else {
		        		List<Object> tdList2 = ((HtmlTableRow) trList2.get(i)).getByXPath("td");
		        		for(int k = 1; k < tdList2.size()-2; k++) {
		        			p.print(((HtmlTableDataCell) tdList2.get(k)).asText()+",");
		        		}
		        		p.println(((HtmlTableDataCell) tdList2.get(tdList2.size()-2)).asText());
		        	}
		        }
	        }
	        
	        	
	        	
	        	
	        p.close();
	        	        
	        webClient.close();

	    }
	}
}
