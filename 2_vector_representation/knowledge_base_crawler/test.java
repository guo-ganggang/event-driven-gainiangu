package test;
 
import java.io.BufferedReader;
import java.io.File;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.PrintStream;
import java.util.List;

import com.gargoylesoftware.htmlunit.WebClient;
import com.gargoylesoftware.htmlunit.html.HtmlPage;
import com.gargoylesoftware.htmlunit.html.HtmlTableBody;
import com.gargoylesoftware.htmlunit.html.HtmlTableDataCell;

public class test {
	public static void main(String args[]) throws Exception {
		test test1 = new test();
		test1.readUrl();
	}
	
	public void readUrl() throws Exception {
		File input = new File("J:/crawl/jinrongjie_first_letters.csv");
		@SuppressWarnings("resource")
		BufferedReader br = new BufferedReader(new FileReader(input));
		String line = br.readLine();
		while(line != null) {
			String abbr = line.split("\t")[1];
			String url = "http://stock.jrj.com.cn/concept/conceptdetail/conceptDetail_"+abbr+".shtml";
			homePage(url, abbr);
			line = br.readLine();
		}
	}
	
	public void homePage(String url, String abbr) throws Exception {
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
	        webClient.waitForBackgroundJavaScript(10000);  
	        
	        HtmlTableBody table=(HtmlTableBody)page.getElementById("stockTbody");
	        
	        List<Object> tdList = table.getByXPath("tr/td");
	        
	        FileOutputStream out=new FileOutputStream("J:\\crawl\\output\\jrj\\"+abbr+".csv");
            @SuppressWarnings("resource")
			PrintStream p = new PrintStream(out);
            
	        
	        for(int i=0; i<tdList.size(); i++) {
	        	p.print(((HtmlTableDataCell) tdList.get(i)).asText());
	        	if((i+1)%8==0)
	        		p.println();
	        	else
	        		p.print(",");
	        }
	        p.close();
	        webClient.close();

	    }
	}
}