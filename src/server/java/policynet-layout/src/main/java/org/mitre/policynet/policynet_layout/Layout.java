package org.mitre.policynet.policynet_layout;

import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.PrintStream;
import java.io.PrintWriter;
import java.io.StringReader;
import java.io.StringWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;

import javax.xml.transform.TransformerConfigurationException;


import org.gephi.graph.api.GraphController;
import org.gephi.graph.api.GraphModel;
import org.gephi.graph.api.Node;
import org.gephi.graph.api.UndirectedGraph;
import org.gephi.io.importer.api.Container;
import org.gephi.io.importer.api.ImportController;
import org.gephi.io.processor.plugin.DefaultProcessor;
import org.gephi.layout.plugin.force.StepDisplacement;
import org.gephi.layout.plugin.force.yifanHu.YifanHuLayout;
import org.gephi.project.api.ProjectController;
import org.gephi.project.api.Workspace;
import org.gephi.statistics.plugin.Degree;
import org.jgrapht.alg.ConnectivityInspector;
import org.jgrapht.ext.EdgeNameProvider;
import org.jgrapht.ext.GraphMLExporter;
import org.jgrapht.ext.VertexNameProvider;
import org.jgrapht.graph.DefaultWeightedEdge;
import org.jgrapht.graph.UndirectedWeightedSubgraph;
import org.jgrapht.graph.WeightedPseudograph;
import org.openide.util.Lookup;
import org.xml.sax.SAXException;

import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;

public class Layout {
	private static Gson gson=new Gson();
	private static double overallStartTime;
	private static PrintStream originalOutStream = System.out;
	private static PrintStream originalErrStream = System.err;
	private static PrintStream dummyStream = new PrintStream(new OutputStream(){
		public void write(int b){
			// do nothing
		}
	});
	private static OutputObj output = new OutputObj();

	public static void main(String[] args){
		nodeStream();
//		fromFile();
	}

	public static void fromFile(){
		try{
	    	List<String> lines = Files.readAllLines(Paths.get("src/sample.json"));
	    	taskRunner(lines.get(0));
	    	System.out.println(gson.toJson(output));
		} catch (Exception e){
			e.printStackTrace();
		}
	}

	public static void nodeStream() {
		ServerSocket server;
		Socket client;
		InputStream input;
		try {
			server = new ServerSocket(0);
			System.out.print("ready:"+server.getLocalPort());
			client = server.accept();
			input = client.getInputStream();
			String inputString = Layout.inputStreamAsString(input);

			System.setOut(dummyStream);
			System.setErr(dummyStream);

	    	taskRunner(inputString);
	    	System.setOut(originalOutStream);
	    	System.setErr(originalErrStream);
	    	System.out.println(gson.toJson(output));

			client.close();
			server.close();
		}
		catch (Exception e) {
			e.printStackTrace();
		}

	}

	public static void toFile(String string, String file){
		try {
			PrintWriter out = new PrintWriter(file);
			out.println(string);
			out.close();
		} catch (FileNotFoundException e) {
			e.printStackTrace();
		}
	}
	
	public static void gephiStatistics(String graphml) {
		ProjectController pc = Lookup.getDefault().lookup(ProjectController.class);
		pc.newProject();
		Workspace workspace = pc.getCurrentWorkspace();

		ImportController importController = Lookup.getDefault().lookup(ImportController.class);
		GraphModel graphModel = Lookup.getDefault().lookup(GraphController.class).getGraphModel(workspace);
		StringReader stringReader = new StringReader(graphml);

		Container container = importController.importFile(stringReader, importController.getFileImporter(".graphml"));

		importController.process(container, new DefaultProcessor(), workspace);

		Degree degree = new Degree();
		degree.execute(graphModel);
		
		output.setAverageDegree(degree.getAverageDegree());

	}

	public static void gephiLayout(String graphml, String layout) {
		ProjectController pc = Lookup.getDefault().lookup(ProjectController.class);
		pc.newProject();
		Workspace workspace = pc.getCurrentWorkspace();

		ImportController importController = Lookup.getDefault().lookup(ImportController.class);
		GraphModel graphModel = Lookup.getDefault().lookup(GraphController.class).getGraphModel();

		StringReader stringReader = new StringReader(graphml);
		Container container = null;
		UndirectedGraph undirectedGraph = graphModel.getUndirectedGraph();
		container = importController.importFile(stringReader, importController.getFileImporter(".graphml"));
		importController.process(container, new DefaultProcessor(), workspace);


//		FruchtermanReingold layout = new FruchtermanReingold(null);
//		ForceAtlas2 layout = new ForceAtlas2(null);
		if (layout.equals("yifanhu")){
			YifanHuLayout layoutObj = new YifanHuLayout (null, new StepDisplacement(1f));
	        layoutObj.setGraphModel(graphModel);
	        layoutObj.initAlgo();
	        layoutObj.resetPropertiesValues();
	        layoutObj.setOptimalDistance(100f);
	   
	        double maxTime = 180 * 1e9;
	        long startTime = System.nanoTime();
	        while (layoutObj.canAlgo() && !layoutObj.isConverged() && (System.nanoTime() - startTime) < maxTime){
	        	layoutObj.goAlgo();
	        }
	        layoutObj.endAlgo();
		} 
		
        for (Node n : undirectedGraph.getNodes()){
        	output.addPosition(n.getLabel(), n.x(), n.y());
        }

	}
	
	
	public static WeightedPseudograph<String, DefaultWeightedEdge> parseGraph(List<ParsedEdge> edges){
		WeightedPseudograph<String, DefaultWeightedEdge> graph = new WeightedPseudograph<String, DefaultWeightedEdge>(DefaultWeightedEdge.class);
		String nid, mid;
		List<String> nidList = new ArrayList<String>();
		DefaultWeightedEdge weightedEdge = null;
		for (ParsedEdge edge : edges){

			nid = edge.getSource();
			if (!nidList.contains(nid)) {
				graph.addVertex(nid);
				nidList.add(nid);
			}
			mid = edge.getTarget();
			if (!nidList.contains(mid)) {
				graph.addVertex(mid);
				nidList.add(mid);
			}
			weightedEdge = graph.addEdge(nid, mid);
			graph.setEdgeWeight(weightedEdge, edge.get_weight());
		}
		return graph;
	}

	public static GraphMLExporter<String, DefaultWeightedEdge> getExporter(){
		VertexNameProvider<String> vertexIDProvider = new VertexNameProvider<String>(){
			public String getVertexName(String vertex){
				return vertex;
			}
		};
		EdgeNameProvider<DefaultWeightedEdge> edgeIDProvider = new EdgeNameProvider<DefaultWeightedEdge>(){
			public String getEdgeName(DefaultWeightedEdge edge){
				return edge.toString();
			}
		};
		GraphMLExporter<String, DefaultWeightedEdge> exporter = new GraphMLExporter<String, DefaultWeightedEdge>(vertexIDProvider, null, edgeIDProvider, null);
		return exporter;
	}
	
	public static void layoutConnectedComponents(WeightedPseudograph<String, DefaultWeightedEdge> graph, String layout){
		ConnectivityInspector<String, DefaultWeightedEdge> connectivityInspector = new ConnectivityInspector<String, DefaultWeightedEdge>(graph);
		List<Set<String>> connectedComponents = connectivityInspector.connectedSets();
		GraphMLExporter<String, DefaultWeightedEdge> exporter = getExporter();
		
		StringWriter writer = new StringWriter();
		output.setCcTime((System.nanoTime() - overallStartTime)/1e9);
		overallStartTime = System.nanoTime();
		try {
			for (Set<String> nodeSet : connectedComponents){
				if (nodeSet.size() == 1){
					String[] nodeArray = nodeSet.toArray(new String[nodeSet.size()]);
					output.addPosition(nodeArray[0], (float) 0, (float) 0);
				} else if (nodeSet.size() == 2){
					String[] nodeArray = nodeSet.toArray(new String[nodeSet.size()]);
					output.addPosition(nodeArray[0], (float) 0, (float) 0);
					output.addPosition(nodeArray[1], (float) 130, (float) 0);
				} else if (nodeSet.size() > 2){
					UndirectedWeightedSubgraph<String, DefaultWeightedEdge> subgraph = new UndirectedWeightedSubgraph<String, DefaultWeightedEdge>(graph, nodeSet, null);
					exporter.export(writer, subgraph);
					gephiLayout(writer.toString(), layout);
					writer.getBuffer().setLength(0);
				} else {
					System.err.println("Node Size isn't 1, 2, or greater 2");
				}
			}
			
			exporter.export(writer, graph);
			gephiStatistics(writer.toString());

		} catch (SAXException e) {
			e.printStackTrace();
		} catch (TransformerConfigurationException e) {
			e.printStackTrace();
		}
		output.setConnectedComponents(connectedComponents);
	}
	
	public static void layoutWhole(WeightedPseudograph<String, DefaultWeightedEdge> graph, String layout){
		GraphMLExporter<String, DefaultWeightedEdge> exporter = getExporter();
		StringWriter writer = new StringWriter();
		output.setCcTime((System.nanoTime() - overallStartTime)/1e9);
		overallStartTime = System.nanoTime();
		try {
			exporter.export(writer, graph);
			gephiLayout(writer.toString(), layout);
			gephiStatistics(writer.toString());
			writer.getBuffer().setLength(0);
						
		} catch (SAXException e) {
			e.printStackTrace();
		} catch (TransformerConfigurationException e) {
			e.printStackTrace();
		}
	}
	public static void taskRunner(String input_json){
		overallStartTime = System.nanoTime();
		InputObj inputObj = gson.fromJson(input_json, new TypeToken<InputObj>(){}.getType());
		List<ParsedEdge> edges = inputObj.getEdges();
		Map<String, String> config = inputObj.getConfig();
		
		WeightedPseudograph<String, DefaultWeightedEdge> graph = parseGraph(edges);
		if (Boolean.valueOf(config.get("layout_cc"))){
			layoutConnectedComponents(graph, config.get("layout"));
		} else {
			layoutWhole(graph, config.get("layout"));
		}
		
		output.setLayoutTime((System.nanoTime() - overallStartTime)/1e9);
		output.setNodes(graph.vertexSet().size());
		output.setEdges(graph.edgeSet().size());
		output.setWeightedAverageDegree(graph.edgeSet().size() * 2.0 / graph.vertexSet().size());
		
	}

	public static String inputStreamAsString(InputStream stream) throws IOException {
		BufferedReader br = new BufferedReader(new InputStreamReader(stream));
		StringBuilder sb = new StringBuilder();
		String line = null;

		while ((line = br.readLine()) != null) {
			sb.append(line + "\n");
		}

		br.close();
		return sb.toString();
	}
}
