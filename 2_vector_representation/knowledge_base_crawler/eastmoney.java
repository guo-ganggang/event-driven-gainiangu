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
import com.gargoylesoftware.htmlunit.html.HtmlTable;
import com.gargoylesoftware.htmlunit.html.HtmlTableBody;
import com.gargoylesoftware.htmlunit.html.HtmlTableDataCell;
import com.gargoylesoftware.htmlunit.html.HtmlTableRow;

public class eastmoney {
	public static void main(String args[]) throws Exception {
		eastmoney test1 = new eastmoney();
		test1.homePage();
	}
	
	public void readUrl() throws Exception {
		File input = new File("J:/crawl/jinrongjie_first_letters.csv");
		@SuppressWarnings("resource")
		BufferedReader br = new BufferedReader(new FileReader(input));
		String line = br.readLine();
		while(line != null) {
			String abbr = line.split("\t")[1];
			String url = "http://stock.jrj.com.cn/concept/conceptdetail/conceptDetail_"+abbr+".shtml";
			homePage();
			line = br.readLine();
		}
	}
	
	public void homePage() throws Exception {
	    try (final WebClient webClient = new WebClient()) {
	        String url = "http://quote.eastmoney.com/center/BKList.html#notion_0_0?sortRule=0";
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
	        webClient.waitForBackgroundJavaScript(10000);  
	        
	        HtmlTable table = (HtmlTable)page.getElementById("bklist");
	        
	        List<Object> trList = table.getByXPath("tbody/tr");
	        
	         
	        
	        for(int i=53; i<trList.size(); i++) {
	        	HtmlAnchor a = (HtmlAnchor) ((HtmlTableRow)trList.get(i)).getByXPath("td/a").get(0);
	        	
	        	FileOutputStream out=new FileOutputStream("J:\\crawl\\output\\eastmoney\\"+a.asText()+".csv");
	            PrintStream p = new PrintStream(out); 
	            
	        	//System.out.println(a.asText());
	        	
	        	HtmlPage newPage = a.click();
	        	webClient.waitForBackgroundJavaScript(10000); 
	        	
	        	HtmlTable newTable = (HtmlTable)newPage.getElementById("fixed");
	        	List<Object> newTrList = newTable.getByXPath("tbody/tr");
	        	
	        	for(int j=1; j<newTrList.size(); j++) {
	        		HtmlTableDataCell td1 = (HtmlTableDataCell) ((HtmlTableRow)newTrList.get(j)).getByXPath("td").get(1);
	        		HtmlTableDataCell td2 = (HtmlTableDataCell) ((HtmlTableRow)newTrList.get(j)).getByXPath("td").get(2);
	        		p.println(td1.asText()+","+td2.asText());
	        	}
	        	
	        	
	        	
	        	while(true) {
	        		HtmlDivision div = (HtmlDivision)newPage.getElementById("pagenav");
	        		List<Object> aList = div.getByXPath("a");
	        		if(aList.size() <= 0)
	        			break;
	        		int size = aList.size();
	        		HtmlAnchor a2 =  (HtmlAnchor)aList.get(size-1);
	        		//p.println(a2.asXml());
	        		if(a2.asText().length()>=3) {
	        			newPage = a2.click();
	    	        	webClient.waitForBackgroundJavaScript(10000); 
	    	        	
	    	        	newTable = (HtmlTable)newPage.getElementById("fixed");
	    	        	newTrList = newTable.getByXPath("tbody/tr");
	    	        	
	    	        	for(int j=1; j<newTrList.size(); j++) {
	    	        		HtmlTableDataCell td1 = (HtmlTableDataCell) ((HtmlTableRow)newTrList.get(j)).getByXPath("td").get(1);
	    	        		HtmlTableDataCell td2 = (HtmlTableDataCell) ((HtmlTableRow)newTrList.get(j)).getByXPath("td").get(2);
	    	        		p.println(td1.asText()+","+td2.asText());
	    	        	}
	        		}
	        		else
	        			break;
	        	}
	        	
	        	p.close();
	        	
//	        	p.print(((HtmlTableDataCell) trList.get(i)).asText());
//	        	if((i+1)%8==0)
//	        		p.println();
//	        	else
//	        		p.print(",");
	        }
//	        
	        webClient.close();

	    }
	}
}